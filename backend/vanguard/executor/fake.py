"""A fake browser over a tiny in-memory site, for tests and offline rehearsal.

Pages are a dict of path -> (text, links). Focus moves through the links with Tab, and
Enter follows the focused link. click(ref) follows the link with that ref directly.
Input events are recorded as a real page listener would, so the checker can be tested.
"""

from dataclasses import dataclass, field

from vanguard.contracts import (
    Action,
    BrowserEvent,
    Observation,
    PerceptionMode,
    PersonaSpec,
    Site,
    Task,
    Tool,
    ToolGroup,
)

from .base import ExecutionResult


@dataclass
class FakePage:
    text: str
    links: list[str] = field(default_factory=list)  # paths


DEFAULT_SITE = {
    "/": FakePage("Tallowmere candles. Dusk Ember $18.00", ["/product/dusk-ember"]),
    "/product/dusk-ember": FakePage("Dusk Ember $18.00 Add to cart", ["/cart"]),
    "/cart": FakePage("Your cart: Dusk Ember x1", ["/checkout"]),
    "/checkout": FakePage("Payment. Pay with the sandbox test card", ["/thanks/fake-order"]),
    "/thanks/fake-order": FakePage("Thank you", []),
}


class FakeExecutor:
    def __init__(self, pages: dict[str, FakePage] | None = None):
        self.pages = pages or DEFAULT_SITE
        self.origin = ""
        self.path = "/"
        self.focus = -1  # index into the current page's links

    async def start(self, site: Site, task: Task, persona: PersonaSpec) -> None:
        self.origin = site.origin
        self.path = task.start_path
        self.focus = -1

    def _page(self) -> FakePage:
        return self.pages.get(self.path, FakePage("Not found"))

    async def observe(self) -> Observation:
        page = self._page()
        lines = [page.text] + [f"[e{i}] link -> {link}" for i, link in enumerate(page.links)]
        if self.focus >= 0:
            lines.append(f"focused: e{self.focus}")
        return Observation(
            mode=PerceptionMode.FULL,
            url=self.origin + self.path,
            content="\n".join(lines),
            links=[self.origin + link for link in page.links],
        )

    def _go(self, path: str) -> None:
        self.path, self.focus = path, -1

    async def execute(self, action: Action) -> ExecutionResult:
        page = self._page()
        events: list[BrowserEvent] = []
        error = None
        if action.group is ToolGroup.POINTER:
            events.append(BrowserEvent(type="pointerdown", trusted=True, target=action.ref))
            if action.tool is Tool.CLICK and action.ref and action.ref.startswith("e"):
                index = int(action.ref[1:])
                if index < len(page.links):
                    self._go(page.links[index])
                else:
                    error = f"no element {action.ref}"
        elif action.tool is Tool.PRESS:
            events.append(BrowserEvent(type="keydown", trusted=True, target=action.key))
            if action.key == "Tab" and page.links:
                self.focus = (self.focus + 1) % len(page.links)
            elif action.key == "Enter" and self.focus >= 0:
                self._go(page.links[self.focus])
        elif action.tool is Tool.GOTO and action.url:
            path = action.url.removeprefix(self.origin) or "/"
            self._go(path)
        return ExecutionResult(
            events=events,
            url_after=self.origin + self.path,
            focus_after=f"e{self.focus}" if self.focus >= 0 else None,
            error=error,
        )

    async def announce(self, action: Action, message: str, tone: str) -> None:
        return None

    async def current_url(self) -> str:
        return self.origin + self.path

    async def page_text(self) -> str:
        return self._page().text

    async def close(self) -> None:
        return None
