"""Screen-reader perception and commands for the L2 persona (docs/leakage-spec.md, L2).

Perception is Chromium's own accessibility tree (CDP Accessibility.getFullAXTree): the
roles, names and states a screen reader would announce, in reading order, with nothing
visual. Elements get ids a1, a2, ... (separate from the full view's e1, e2, ...).

Commands emulate a screen reader's virtual cursor, in the spirit of TaskAudit's
screen-reader proxy: sr_next / sr_prev move the cursor to the next element of a kind
(focusing it when it is focusable, as screen readers do), sr_read reads the current
element, and sr_activate sends Enter (or Space for toggles) to it as real key presses.
Nodes hidden from assistive technology (aria-hidden, the Vanguard HUD) never appear.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from playwright.async_api import CDPSession, Page

KIND_ROLES: dict[str, set[str]] = {
    "heading": {"heading"},
    "link": {"link"},
    "button": {"button", "menuitem", "tab"},
    "form_field": {
        "textbox",
        "searchbox",
        "combobox",
        "listbox",
        "checkbox",
        "radio",
        "switch",
        "slider",
        "spinbutton",
    },
    "landmark": {
        "banner",
        "navigation",
        "main",
        "contentinfo",
        "complementary",
        "region",
        "search",
        "form",
    },
    "list_item": {"listitem"},
}
SKIP_ROLES = {
    "none",
    "generic",
    "InlineTextBox",
    "LineBreak",
    "presentation",
    "RootWebArea",
    "paragraph",
}
# Controls whose name already carries their text: text inside them is not repeated.
NAMED_BY_CONTENT = {"link", "button", "heading", "menuitem", "tab", "option", "listitem"}
TOGGLES = {"checkbox", "radio", "switch"}
STATES = ("focused", "checked", "expanded", "pressed", "selected", "disabled", "required", "level")
MAX_LINES = 400


@dataclass
class AxItem:
    ref: str
    role: str
    name: str
    backend_id: int | None
    states: dict[str, object] = field(default_factory=dict)

    def announce(self) -> str:
        if self.role == "StaticText":
            return self.name
        parts = [self.role]
        if self.role == "heading" and "level" in self.states:
            parts = [f"heading level {self.states['level']}"]
        if self.name:
            parts.append(f'"{self.name}"')
        for state in ("checked", "expanded", "pressed", "selected"):
            if state in self.states:
                parts.append(f"{state}={self.states[state]}")
        for flag in ("disabled", "required"):
            if self.states.get(flag):
                parts.append(flag)
        return " ".join(parts)


def _value(entry: dict | None):
    return (entry or {}).get("value")


def linearise(nodes: list[dict]) -> list[AxItem]:
    """Non-ignored nodes in document (depth-first) order, without layout-only roles."""
    by_id = {node["nodeId"]: node for node in nodes}
    children = {node["nodeId"]: node.get("childIds", []) for node in nodes}
    roots = [node for node in nodes if not node.get("parentId")]
    items: list[AxItem] = []
    # (node id, whether an ancestor already announces this text)
    stack = [(root["nodeId"], False) for root in reversed(roots)]
    while stack and len(items) < MAX_LINES:
        node_id, named_above = stack.pop()
        node = by_id.get(node_id)
        if node is None:
            continue
        role = str(_value(node.get("role")) or "")
        name = " ".join(str(_value(node.get("name")) or "").split())
        announces = not node.get("ignored") and role in NAMED_BY_CONTENT and bool(name)
        stack.extend(
            (child, named_above or announces) for child in reversed(children.get(node_id, []))
        )
        if node.get("ignored"):
            continue
        if role in SKIP_ROLES or (role == "StaticText" and (not name or named_above)):
            continue
        states = {
            prop["name"]: _value(prop.get("value"))
            for prop in node.get("properties", [])
            if prop.get("name") in STATES
        }
        items.append(AxItem(f"a{len(items) + 1}", role, name, node.get("backendDOMNodeId"), states))
    return _drop_echoed_text(items)


def _drop_echoed_text(items: list[AxItem]) -> list[AxItem]:
    """A link or button announces its text already; drop the text node that repeats it."""
    kept: list[AxItem] = []
    for item in items:
        previous = kept[-1] if kept else None
        if (
            item.role == "StaticText"
            and previous is not None
            and previous.role != "StaticText"
            and item.name
            and item.name in previous.name
        ):
            continue
        kept.append(item)
    for number, item in enumerate(kept, start=1):
        item.ref = f"a{number}"
    return kept


class ScreenReader:
    def __init__(self, page: Page):
        self.page = page
        self._cdp: CDPSession | None = None
        self.items: list[AxItem] = []
        self.cursor: int = -1  # index into items
        self._url = ""
        self._focused_node: int | None = None

    async def _session(self) -> CDPSession:
        if self._cdp is None:
            self._cdp = await self.page.context.new_cdp_session(self.page)
            await self._cdp.send("Accessibility.enable")
        return self._cdp

    async def refresh(self) -> list[AxItem]:
        cdp = await self._session()
        tree = await cdp.send("Accessibility.getFullAXTree")
        cursor_node = self.current.backend_id if self.current else None
        self.items = linearise(tree.get("nodes", []))
        if self.page.url != self._url:  # a new page: the cursor starts at the top
            self._url = self.page.url
            self.cursor = -1
        elif cursor_node is not None:
            self.cursor = next(
                (i for i, item in enumerate(self.items) if item.backend_id == cursor_node), -1
            )
        focused = next((i for i, it in enumerate(self.items) if it.states.get("focused")), None)
        focused_node = self.items[focused].backend_id if focused is not None else None
        if focused is not None and focused_node != self._focused_node:
            self.cursor = focused  # screen readers follow keyboard focus when it moves
        self._focused_node = focused_node
        return self.items

    @property
    def current(self) -> AxItem | None:
        return self.items[self.cursor] if 0 <= self.cursor < len(self.items) else None

    def render(self, title: str) -> str:
        lines = [f"Page title: {title}"] if title else []
        for index, item in enumerate(self.items):
            marker = "> " if index == self.cursor else ""
            lines.append(f"{marker}[{item.ref}] {item.announce()}")
        current = self.current
        lines.append(
            f"Screen reader cursor: {current.ref} {current.announce()}"
            if current
            else "Screen reader cursor: top of the page"
        )
        return "\n".join(lines)

    async def move(self, kind: str, step: int) -> str | None:
        """Move the virtual cursor to the next (step=1) or previous (-1) element of a kind."""
        await self.refresh()
        roles = KIND_ROLES.get(kind, set())
        index = self.cursor
        while True:
            index += step
            if not 0 <= index < len(self.items):
                return f"no {kind.replace('_', ' ')} {'after' if step > 0 else 'before'} here"
            if self.items[index].role in roles:
                break
        self.cursor = index
        await self._focus(self.items[index])
        return None

    async def _focus(self, item: AxItem) -> None:
        if item.backend_id is None:
            return
        try:
            cdp = await self._session()
            await cdp.send("DOM.focus", {"backendNodeId": item.backend_id})
        except Exception:  # not focusable: the virtual cursor moves on its own
            pass

    async def activate(self) -> str | None:
        await self.refresh()
        item = self.current
        if item is None:
            return "nothing under the screen reader cursor"
        await self._focus(item)
        await self.page.keyboard.press("Space" if item.role in TOGGLES else "Enter")
        return None

    async def box(self) -> dict | None:
        """Bounding box of the cursor element, for the step record and the HUD."""
        item = self.current
        if item is None or item.backend_id is None:
            return None
        try:
            cdp = await self._session()
            model = await cdp.send("DOM.getBoxModel", {"backendNodeId": item.backend_id})
        except Exception:
            return None
        quad = model["model"]["border"]
        xs, ys = quad[0::2], quad[1::2]
        return {"x": min(xs), "y": min(ys), "width": max(xs) - min(xs), "height": max(ys) - min(ys)}
