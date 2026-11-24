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

The HUD (apps/hud) is decoration for people watching a run. It is excluded from the
text observation, but it does appear in the saved screenshots and its ring marks the
focused element even where the site hides focus. Screenshots are therefore for people
only; a screenshot-based perception for the model must hide the HUD first.
"""

from __future__ import annotations

import asyncio
import base64
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
    Condition,
    Observation,
    PerceptionMode,
    PersonaSpec,
    Rect,
    Site,
    Task,
    Tool,
    ToolGroup,
)

from .base import ExecutionResult
from .screen_reader import ScreenReader

if TYPE_CHECKING:
    from playwright.async_api import Browser, BrowserContext, ElementHandle, Page, Playwright, Route

    from vanguard.settings import Settings

log = logging.getLogger(__name__)

_JS = files("vanguard.executor") / "js"
OBSERVE_JS = (_JS / "observe.js").read_text(encoding="utf-8")
LISTEN_JS = (_JS / "listen.js").read_text(encoding="utf-8")
# Built from apps/hud (npm run build). Decoration only; see that package.
HUD_JS = (_JS / "hud.js").read_text(encoding="utf-8")
HUD_SHOW = """([character, label, box, text, tone]) => {
    const hud = window[Symbol.for('vanguard.hud')];
    if (!hud) return false;
    hud.show(character, label, box, text, tone);
    return true;
}"""
FOCUS_BOX = """() => {
    const el = document.activeElement;
    if (!el || el === document.body || el === document.documentElement) return null;
    const r = el.getBoundingClientRect();
    return { x: r.x, y: r.y, width: r.width, height: r.height };
}"""
HUD_WALK_MS = 450
BINDING = "__vanguardRecord"

VIEWPORT = {"width": 1280, "height": 720}
# Conditions (leakage-spec Section 4): never leakage, they change success, steps and latency.
MOBILE = {
    "viewport": {"width": 390, "height": 844},
    "device_scale_factor": 3,
    "is_mobile": True,
    "has_touch": True,
    "user_agent": (
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 "
        "(KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
    ),
}
# Roughly a slow 3G connection: 400 ms latency, 500 kbit/s down and up.
SLOW_NETWORK = {
    "offline": False,
    "latency": 400,
    "downloadThroughput": 500 * 1024 / 8,
    "uploadThroughput": 500 * 1024 / 8,
}
ACTION_TIMEOUT_MS = 5000
SETTLE_MS = 400
IDLE_TIMEOUT_MS = 2500
NAVIGATION_MS = 8000
MAX_OBSERVATION_CHARS = 9000

DEFAULT_ZOOM = 4.0


def _caption(action: Action) -> str:
    args = action.model_dump(exclude={"tool", "rationale"}, exclude_none=True)
    shown = ", ".join(f"{value}" for value in args.values())
    return f"{action.tool} {shown}".strip()


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
        conditions: list[Condition] | None = None,
        bounded_perception: bool = False,
        live_path: Path | None = None,
    ):
        # Option 3: perceive only what the persona's mode allows (Section 5 of the spec).
        self.bounded_perception = bounded_perception
        self._reader: ScreenReader | None = None
        self._perception = PerceptionMode.FULL
        self._window: Rect | None = None  # the magnifier's view, document coordinates
        self._zoom = DEFAULT_ZOOM
        self._page_size = (0.0, 0.0)
        self._focus_rect: Rect | None = None
        self.conditions = set(conditions or [])
        from vanguard import origins  # catalog sites are always allowed

        self.allowed_origins = {_origin(o) for o in origins.allowed_origins(settings)}
        self.payment_hosts = {host.lower() for host in settings.allowed_payment_hosts}
        self.headless = settings.headless if headless is None else headless
        self.rewrites = {
            _origin(source): target.rstrip("/")
            for source, target in origins.rewrites(settings).items()
        }
        if screenshot_dir is None and settings.screenshots:
            screenshot_dir = Path(settings.data_dir) / "screenshots"
        self.screenshot_dir = screenshot_dir
        self.hud = settings.hud
        self._character: tuple[str, str] | None = None
        self.session = uuid.uuid4().hex[:12]
        self.blocked: list[str] = []  # request URLs aborted by the network filter
        # Live view (vanguard.live): screencast frames are written here while the run goes.
        self.live_path = live_path
        self._screencast = None

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
        options: dict = {"viewport": VIEWPORT}
        if Condition.MOBILE in self.conditions:
            options = dict(MOBILE)
        self._context = await self._browser.new_context(locale="en-US", **options)
        await self._context.route("**/*", self._filter)
        await self._context.expose_binding(BINDING, self._record)
        await self._context.add_init_script(LISTEN_JS)
        if self.hud and persona is not None:
            await self._context.add_init_script(HUD_JS)
            self._character = (persona.character, f"{persona.name} · Vanguard test")
        self._page = await self._context.new_page()
        self._page.set_default_timeout(ACTION_TIMEOUT_MS)
        self._reader = ScreenReader(self._page)
        if (
            self.bounded_perception
            and persona is not None
            and persona.perception is PerceptionMode.ACCESSIBILITY_TREE
        ):
            self._perception = PerceptionMode.ACCESSIBILITY_TREE
        if (
            self.bounded_perception
            and persona is not None
            and persona.perception is PerceptionMode.MAGNIFIED
        ):
            self._perception = PerceptionMode.MAGNIFIED
            self._zoom = persona.magnification or DEFAULT_ZOOM
            size = self._page.viewport_size or VIEWPORT
            self._window = Rect(
                x=0, y=0, width=size["width"] / self._zoom, height=size["height"] / self._zoom
            )
        if self.live_path is not None:
            await self._start_screencast()
        if Condition.SLOW_NETWORK in self.conditions:
            cdp = await self._context.new_cdp_session(self._page)
            await cdp.send("Network.enable")
            await cdp.send("Network.emulateNetworkConditions", SLOW_NETWORK)
        await self._page.goto(site.origin + task.start_path, wait_until="domcontentloaded")
        await self._settle()

    async def _start_screencast(self) -> None:
        """Stream the page to the live-view file. Never fails the run: without a
        screencast the run page falls back to the step screenshots."""
        from vanguard import live

        try:
            cdp = await self._context.new_cdp_session(self._page)

            def on_frame(params: dict) -> None:
                live.write_frame(self.live_path, base64.b64decode(params["data"]))
                asyncio.ensure_future(
                    cdp.send("Page.screencastFrameAck", {"sessionId": params["sessionId"]})
                )

            cdp.on("Page.screencastFrame", on_frame)
            await cdp.send(
                "Page.startScreencast",
                {
                    "format": "jpeg",
                    "quality": live.FRAME_QUALITY,
                    "maxWidth": live.MAX_WIDTH,
                    "maxHeight": live.MAX_HEIGHT,
                },
            )
            self._screencast = cdp
        except Exception:
            self._screencast = None

    async def close(self) -> None:
        if self._screencast is not None:
            try:
                await self._screencast.send("Page.stopScreencast")
            except Exception:  # the page is already gone
                pass
            self._screencast = None
        if self.live_path is not None:
            from vanguard import live

            live.clear(self.live_path)
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
        self._page_size = (data["page"]["width"], data["page"]["height"])
        self._focus_rect = Rect(**focus["box"]) if focus and focus.get("box") else None
        links = data["links"]
        if focus and focus["inFrame"]:
            lines.append("Keyboard focus: inside an embedded frame (its contents are not shown)")
        elif focus and focus["visible"]:
            lines.append(f"Keyboard focus: {focus['ref']}")
        content = "\n".join(lines)
        if self._perception is PerceptionMode.MAGNIFIED and self._window is not None:
            content, links = self._magnified(data)
        if self._perception is PerceptionMode.ACCESSIBILITY_TREE and self._reader is not None:
            await self._reader.refresh()
            content = self._reader.render(data["title"])
        if len(content) > MAX_OBSERVATION_CHARS:
            content = content[:MAX_OBSERVATION_CHARS] + "\n(page continues; scroll to see more)"

        screenshot = None
        if self.screenshot_dir is not None:
            self._observations += 1
            path = self.screenshot_dir / self.session / f"{self._observations:03d}.png"
            path.parent.mkdir(parents=True, exist_ok=True)
            if self._window is not None:  # what the magnifier shows, not the whole page
                await self.page.screenshot(
                    path=str(path), full_page=True, clip=self._window.model_dump()
                )
            else:
                await self.page.screenshot(path=str(path))
            screenshot = str(path)

        return Observation(
            mode=self._perception,
            url=data["url"],
            content=content,
            links=links,
            window=self._window,
            screenshot_path=screenshot,
        )

    def _magnified(self, data: dict) -> tuple[str, list[str]]:
        """Only the lines whose boxes intersect the magnifier window (L3)."""
        window = self._window
        assert window is not None
        width, height = self._page_size
        shown, links = [], []
        for line, box in zip(data["lines"], data["boxes"], strict=True):
            if Rect(**box).intersects(window):
                shown.append(line)
                if " -> " in line and line.startswith("[e"):
                    links.append(urljoin(data["url"], line.rsplit(" -> ", 1)[1]))
        header = (
            f"Magnified view at {self._zoom * 100:.0f}%: you see the region from x={window.x:.0f},"
            f" y={window.y:.0f}, {window.width:.0f} by {window.height:.0f} CSS pixels, of a page"
            f" {width:.0f} by {height:.0f}. Use pan to see other parts."
        )
        body = shown or ["(nothing here but empty space)"]
        focus = data["focus"]
        tail = []
        if focus and focus["visible"] and self._focus_rect and self._focus_rect.intersects(window):
            tail = [f"Keyboard focus: {focus['ref']}"]
        title = [f"Page title: {data['title']}"] if data["title"] else []
        return "\n".join([*title, header, *body, *tail]), links

    def _pan(self, dx: float, dy: float) -> None:
        window = self._window
        assert window is not None
        width, height = self._page_size
        x = min(max(0.0, window.x + dx), max(0.0, width - window.width))
        y = min(max(0.0, window.y + dy), max(0.0, height - window.height))
        self._window = window.model_copy(update={"x": x, "y": y})

    async def _doc_box(self, element: ElementHandle | None) -> Rect | None:
        """The element's box in document coordinates (stable across scrolling)."""
        if element is None:
            return None
        box = await element.evaluate(
            "(el) => { const r = el.getBoundingClientRect();"
            " return { x: r.x + scrollX, y: r.y + scrollY, width: r.width, height: r.height }; }"
        )
        return Rect(**box)

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

    async def _snapshot_focus(self) -> None:
        """Refresh the page size and the focused element's box (both in document pixels)."""
        data = await self._snapshot()
        self._page_size = (data["page"]["width"], data["page"]["height"])
        focus = data["focus"]
        self._focus_rect = Rect(**focus["box"]) if focus and focus.get("box") else None

    # ---------------------------------------------------------------- HUD

    async def _show(self, box: Rect | None, text: str, tone: str) -> None:
        """Walk the character to `box` and say `text`. Never affects the run."""
        if self._character is None:
            return
        try:
            data = box.model_dump() if box else None
            shown = await self.page.evaluate(HUD_SHOW, [*self._character, data, text, tone])
            if shown:
                await self.page.wait_for_timeout(HUD_WALK_MS)
        except Exception:  # decoration must never break a run
            pass

    async def _focus_box(self) -> Rect | None:
        try:
            box = await self.page.evaluate(FOCUS_BOX)
        except Exception:
            return None
        return Rect(**box) if box else None

    async def announce(self, action: Action, message: str, tone: str) -> None:
        """Show an action that did not run (refused) or that ended the run (done)."""
        box = None
        if action.ref:
            box = await self._box(await self._element(action.ref))
        if box is None:
            box = await self._focus_box()
        await self._show(box, message, tone)

    # ---------------------------------------------------------------- actions

    async def execute(self, action: Action) -> ExecutionResult:
        self._events = []
        self._step_began = time.perf_counter()
        target_box = None
        error = None
        if self._character is not None:
            ahead = await self._box(await self._element(action.ref)) if action.ref else None
            await self._show(ahead or await self._focus_box(), _caption(action), "act")
            self._events = []  # the walk is not part of the step
        before = self.page.url
        link = await self._link_target(action)
        try:
            target_box, error = await self._perform(action)
        except Exception as exc:  # reported to the agent as a failed step
            error = f"{type(exc).__name__}: {str(exc).splitlines()[0][:200]}"
        if link and error is None and link.split("#")[0] != before.split("#")[0]:
            # A link was activated: client-side routing (and a dev server compiling the
            # route) can take longer than the settle time, so wait for the URL to change.
            try:
                await self.page.wait_for_url(lambda url: url != before, timeout=NAVIGATION_MS)
            except Exception:  # the link may be handled by script; the step still counts
                pass
        await self._settle()
        if self._character is not None and action.group is ToolGroup.KEYBOARD:
            await self._show(await self._focus_box(), _caption(action), "act")
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

    async def _link_target(self, action: Action) -> str | None:
        """The same-origin link this action will activate, if any (click, or Enter on focus)."""
        script = (
            "(el) => { const a = el && el.closest && el.closest('a[href]');"
            " return a && a.origin === location.origin ? a.href : null; }"
        )
        try:
            if action.tool is Tool.CLICK:
                element = await self._element(action.ref)
                return await element.evaluate(script) if element else None
            if action.tool is Tool.PRESS and action.key == "Enter":
                return await self.page.evaluate(f"({script})(document.activeElement)")
        except Exception:
            return None
        return None

    async def _perform(self, action: Action) -> tuple[Rect | None, str | None]:
        page = self.page
        tool = action.tool
        if tool in (Tool.PAN, Tool.PAN_TO_FOCUS):
            if self._window is None:
                return None, "the magnifier is not on for this run"
            await self._snapshot_focus()  # the page may have grown or changed since
            if tool is Tool.PAN:
                self._pan(action.dx or 0, action.dy or 0)
            else:
                if self._focus_rect is None:
                    return None, "nothing has keyboard focus"
                box, window = self._focus_rect, self._window
                self._pan(
                    box.x + box.width / 2 - (window.x + window.width / 2),
                    box.y + box.height / 2 - (window.y + window.height / 2),
                )
            return None, None

        if tool in (Tool.SR_NEXT, Tool.SR_PREV, Tool.SR_READ, Tool.SR_ACTIVATE):
            reader = self._reader
            if reader is None:
                return None, "the screen reader is not running"
            if tool is Tool.SR_READ:
                await reader.refresh()
                error = None
            elif tool is Tool.SR_ACTIVATE:
                error = await reader.activate()
            else:
                error = await reader.move(action.kind or "", 1 if tool is Tool.SR_NEXT else -1)
            box = await reader.box()
            return (Rect(**box) if box else None), error

        if tool is Tool.PRESS:
            for _ in range(action.repeat or 1):  # each press is a real, recorded keypress
                await page.keyboard.press(action.key or "")
                await page.wait_for_timeout(60)
        elif tool is Tool.TYPE:
            await page.keyboard.type(action.text or "", delay=20)
        elif tool is Tool.CLICK_AT:
            scroll = await page.evaluate("() => [scrollX, scrollY]")
            box = Rect(
                x=(action.x or 0) + scroll[0], y=(action.y or 0) + scroll[1], width=1, height=1
            )
            await page.mouse.click(action.x or 0, action.y or 0)
            return box, None
        elif tool is Tool.WHEEL:
            await page.mouse.wheel(action.dx or 0, action.dy or 0)
        elif tool in (Tool.CLICK, Tool.HOVER, Tool.DRAG):
            element = await self._element(action.ref)
            if element is None:
                return None, f"no element {action.ref} on the page now"
            box = await self._doc_box(element)
            if tool is Tool.CLICK and Condition.MOBILE in self.conditions:
                await element.tap()  # a touch screen: a tap, still recorded as pointer input
            elif tool is Tool.CLICK:
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
