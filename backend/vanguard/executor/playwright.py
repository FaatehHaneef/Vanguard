"""The real executor: Chromium driven from outside the page with Playwright.

Key presses and clicks are genuine browser input (Playwright's keyboard and mouse), so
the input modality of every step is known exactly. The page is never told it is being
tested; two small scripts are added from outside:
  - js/listen.js records trusted input events into the step record (H1's browser check);
  - js/observe.js builds the full-view observation: a numbered element list (e1, e2, ...)
    with role, name and state, the visible text, and the visible links.

Focus is reported to the persona only when it is visibly indicated (leakage-spec.md
Section 9, "invisible focus"). The step record always stores the real focus.

Network requests outside the allowed origins and the sandbox payment hosts are aborted.
"""

from __future__ import annotations

import logging
import time
import uuid
from importlib.resources import files
from pathlib import Path
from typing import TYPE_CHECKING, Any
from urllib.parse import urljoin, urlsplit

from vanguard.contracts import (
    Action,
    BrowserEvent,
    Observation,
    PerceptionMode,
    PersonaSpec,
    Rect,
    Site,
    Task,
    Tool,
)

from .base import ExecutionResult

if TYPE_CHECKING:
    from playwright.async_api import Browser, BrowserContext, ElementHandle, Page, Playwright, Route

    from vanguard.settings import Settings

log = logging.getLogger(__name__)

_JS = files("vanguard.executor") / "js"
OBSERVE_JS = (_JS / "observe.js").read_text(encoding="utf-8")
LISTEN_JS = (_JS / "listen.js").read_text(encoding="utf-8")
BINDING = "__vanguardRecord"

VIEWPORT = {"width": 1280, "height": 720}
ACTION_TIMEOUT_MS = 5000
SETTLE_MS = 400
IDLE_TIMEOUT_MS = 2500
MAX_OBSERVATION_CHARS = 9000

UNSUPPORTED = {
    Tool.SR_NEXT,
    Tool.SR_PREV,
    Tool.SR_READ,
    Tool.SR_ACTIVATE,
    Tool.PAN,
    Tool.PAN_TO_FOCUS,
}


def _origin(url: str) -> str:
    parts = urlsplit(url)
    return f"{parts.scheme}://{parts.netloc}".lower()


class PlaywrightExecutor:
    def __init__(
        self,
        settings: Settings,
        *,
        headless: bool | None = None,
        screenshot_dir: Path | None = None,
    ):
        self.allowed_origins = {_origin(origin) for origin in settings.allowed_origins}
        self.payment_hosts = {host.lower() for host in settings.allowed_payment_hosts}
        self.headless = settings.headless if headless is None else headless
        self.rewrites = {
            _origin(source): target.rstrip("/")
            for source, target in settings.origin_rewrites.items()
        }
        if screenshot_dir is None and settings.screenshots:
            screenshot_dir = Path(settings.data_dir) / "screenshots"
        self.screenshot_dir = screenshot_dir
        self.session = uuid.uuid4().hex[:12]
        self.blocked: list[str] = []  # request URLs aborted by the network filter

        self._playwright: Playwright | None = None
        self._browser: Browser | None = None
        self._context: BrowserContext | None = None
        self._page: Page | None = None
        self._events: list[BrowserEvent] = []
        self._step_began = time.perf_counter()
        self._observations = 0
        self._last_focus: str | None = None

    # ---------------------------------------------------------------- lifecycle

    async def start(self, site: Site, task: Task, persona: PersonaSpec) -> None:
        from playwright.async_api import async_playwright

        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch(headless=self.headless)
        self._context = await self._browser.new_context(viewport=VIEWPORT, locale="en-US")
        await self._context.route("**/*", self._filter)
        await self._context.expose_binding(BINDING, self._record)
        await self._context.add_init_script(LISTEN_JS)
        self._page = await self._context.new_page()
        self._page.set_default_timeout(ACTION_TIMEOUT_MS)
        await self._page.goto(site.origin + task.start_path, wait_until="domcontentloaded")
        await self._settle()

    async def close(self) -> None:
        for closer in (self._context, self._browser):
            if closer is not None:
                try:
                    await closer.close()
                except Exception:  # already gone
                    pass
        if self._playwright is not None:
            await self._playwright.stop()
        self._context = self._browser = self._page = self._playwright = None

    @property
    def page(self) -> Page:
        if self._page is None:
            raise RuntimeError("executor not started")
        return self._page

    # ---------------------------------------------------------------- browser hooks

    def _allowed(self, url: str) -> bool:
        parts = urlsplit(url)
        if parts.scheme not in ("http", "https"):
            return True  # data:, blob: and the like never leave the machine
        if _origin(url) in self.allowed_origins:
            return True
        return (parts.hostname or "").lower() in self.payment_hosts

    async def _filter(self, route: Route) -> None:
        url = route.request.url
        if self._allowed(url):
            origin = _origin(url)
            if origin in self.rewrites:
                await route.continue_(url=self.rewrites[origin] + url[len(origin) :])
            else:
                await route.continue_()
        else:
            self.blocked.append(url)
            log.info("blocked request to %s", url)
            await route.abort("blockedbyclient")

    def _record(self, source: Any, payload: dict) -> None:
        if not isinstance(payload, dict):
            return
        self._events.append(
            BrowserEvent(
                type=str(payload.get("type")),
                trusted=bool(payload.get("trusted")),
                target=payload.get("target"),
                t_ms=(time.perf_counter() - self._step_began) * 1000,
            )
        )

    async def _settle(self) -> None:
        try:
            await self.page.wait_for_load_state("domcontentloaded")
            await self.page.wait_for_load_state("networkidle", timeout=IDLE_TIMEOUT_MS)
        except Exception:  # pages with polling never go idle; that is fine
            pass
        await self.page.wait_for_timeout(SETTLE_MS)

    # ---------------------------------------------------------------- perception

    async def _snapshot(self) -> dict:
        return await self.page.evaluate(OBSERVE_JS)

    async def observe(self) -> Observation:
        data = await self._snapshot()
        self._last_focus = data["focus"]["ref"] if data["focus"] else None
        lines = [f"Page title: {data['title']}"] if data["title"] else []
        lines += data["lines"]
        focus = data["focus"]
        if focus and focus["inFrame"]:
            lines.append("Keyboard focus: inside an embedded frame (its contents are not shown)")
        elif focus and focus["visible"]:
            lines.append(f"Keyboard focus: {focus['ref']}")
        content = "\n".join(lines)
        if len(content) > MAX_OBSERVATION_CHARS:
            content = content[:MAX_OBSERVATION_CHARS] + "\n(page continues; scroll to see more)"

        screenshot = None
        if self.screenshot_dir is not None:
            self._observations += 1
            path = self.screenshot_dir / self.session / f"{self._observations:03d}.png"
            path.parent.mkdir(parents=True, exist_ok=True)
            await self.page.screenshot(path=str(path))
            screenshot = str(path)

        return Observation(
            mode=PerceptionMode.FULL,
            url=data["url"],
            content=content,
            links=data["links"],
            screenshot_path=screenshot,
        )

    async def _element(self, ref: str | None) -> ElementHandle | None:
        if not ref or not ref.startswith("e") or not ref[1:].isdigit():
            return None
        handle = await self.page.evaluate_handle(
            "(i) => (window[Symbol.for('vanguard.refs')] || [])[i] || null", int(ref[1:]) - 1
        )
        element = handle.as_element()
        if element is None or not await element.evaluate("(el) => el.isConnected"):
            return None
        return element

    async def _box(self, element: ElementHandle | None) -> Rect | None:
        if element is None:
            return None
        box = await element.bounding_box()
        return Rect(**box) if box else None

    # ---------------------------------------------------------------- actions

    async def execute(self, action: Action) -> ExecutionResult:
        self._events = []
        self._step_began = time.perf_counter()
        target_box = None
        error = None
        try:
            target_box, error = await self._perform(action)
        except Exception as exc:  # reported to the agent as a failed step
            error = f"{type(exc).__name__}: {str(exc).splitlines()[0][:200]}"
        await self._settle()
        focus = None
        try:
            snapshot = await self._snapshot()  # refreshes refs so focus_after uses new ids
            focus = snapshot["focus"]["ref"] if snapshot["focus"] else None
        except Exception:  # page mid-navigation
            pass
        return ExecutionResult(
            events=list(self._events),
            url_after=self.page.url,
            focus_after=focus,
            target_box=target_box,
            error=error,
        )

    async def _perform(self, action: Action) -> tuple[Rect | None, str | None]:
        page = self.page
        tool = action.tool
        if tool in UNSUPPORTED:
            return None, f"{tool} is not available in this executor yet"

        if tool is Tool.PRESS:
            await page.keyboard.press(action.key or "")
        elif tool is Tool.TYPE:
            await page.keyboard.type(action.text or "", delay=20)
        elif tool is Tool.CLICK_AT:
            box = Rect(x=action.x or 0, y=action.y or 0, width=1, height=1)
            await page.mouse.click(action.x or 0, action.y or 0)
            return box, None
        elif tool is Tool.WHEEL:
            await page.mouse.wheel(action.dx or 0, action.dy or 0)
        elif tool in (Tool.CLICK, Tool.HOVER, Tool.DRAG):
            element = await self._element(action.ref)
            if element is None:
                return None, f"no element {action.ref} on the page now"
            box = await self._box(element)
            if tool is Tool.CLICK:
                await element.click()
            elif tool is Tool.HOVER:
                await element.hover()
            else:
                other = await self._element(action.to_ref)
                if other is None:
                    return box, f"no element {action.to_ref} on the page now"
                await element.hover()
                await page.mouse.down()
                await other.hover()
                await page.mouse.up()
            return box, None
        elif tool is Tool.GOTO:
            url = urljoin(page.url, action.url or "")
            await page.goto(url, wait_until="domcontentloaded")
        elif tool is Tool.BACK:
            await page.go_back(wait_until="domcontentloaded")
        elif tool is Tool.RELOAD:
            await page.reload(wait_until="domcontentloaded")
        return None, None

    # ---------------------------------------------------------------- reads

    async def current_url(self) -> str:
        return self.page.url

    async def page_text(self) -> str:
        try:
            return await self.page.inner_text("body")
        except Exception:
            return ""
