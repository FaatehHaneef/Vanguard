"""The action vocabulary (docs/leakage-spec.md, Section 2).

Every action the agent can propose is one Action. The executor records which tool
ran, so the input modality of each step is known exactly.
"""

from enum import StrEnum

from pydantic import BaseModel, Field, model_validator


class ToolGroup(StrEnum):
    KEYBOARD = "keyboard"
    POINTER = "pointer"
    SCREEN_READER = "screen_reader"
    MAGNIFIER = "magnifier"
    NAVIGATION = "navigation"
    CONTROL = "control"


class Tool(StrEnum):
    PRESS = "press"
    TYPE = "type"
    CLICK = "click"
    CLICK_AT = "click_at"
    HOVER = "hover"
    DRAG = "drag"
    WHEEL = "wheel"
    SR_NEXT = "sr_next"
    SR_PREV = "sr_prev"
    SR_READ = "sr_read"
    SR_ACTIVATE = "sr_activate"
    PAN = "pan"
    PAN_TO_FOCUS = "pan_to_focus"
    GOTO = "goto"
    BACK = "back"
    RELOAD = "reload"
    DONE = "done"
    GIVE_UP = "give_up"


TOOL_GROUPS: dict[Tool, ToolGroup] = {
    Tool.PRESS: ToolGroup.KEYBOARD,
    Tool.TYPE: ToolGroup.KEYBOARD,
    Tool.CLICK: ToolGroup.POINTER,
    Tool.CLICK_AT: ToolGroup.POINTER,
    Tool.HOVER: ToolGroup.POINTER,
    Tool.DRAG: ToolGroup.POINTER,
    Tool.WHEEL: ToolGroup.POINTER,
    Tool.SR_NEXT: ToolGroup.SCREEN_READER,
    Tool.SR_PREV: ToolGroup.SCREEN_READER,
    Tool.SR_READ: ToolGroup.SCREEN_READER,
    Tool.SR_ACTIVATE: ToolGroup.SCREEN_READER,
    Tool.PAN: ToolGroup.MAGNIFIER,
    Tool.PAN_TO_FOCUS: ToolGroup.MAGNIFIER,
    Tool.GOTO: ToolGroup.NAVIGATION,
    Tool.BACK: ToolGroup.NAVIGATION,
    Tool.RELOAD: ToolGroup.NAVIGATION,
    Tool.DONE: ToolGroup.CONTROL,
    Tool.GIVE_UP: ToolGroup.CONTROL,
}

# Arguments each tool needs. Anything else is ignored by the executor.
REQUIRED_ARGS: dict[Tool, tuple[str, ...]] = {
    Tool.PRESS: ("key",),
    Tool.TYPE: ("text",),
    Tool.CLICK: ("ref",),
    Tool.CLICK_AT: ("x", "y"),
    Tool.HOVER: ("ref",),
    Tool.DRAG: ("ref", "to_ref"),
    Tool.WHEEL: ("dx", "dy"),
    Tool.SR_NEXT: ("kind",),
    Tool.SR_PREV: ("kind",),
    Tool.PAN: ("dx", "dy"),
    Tool.GOTO: ("url",),
    Tool.DONE: ("answer",),
    Tool.GIVE_UP: ("reason",),
}

SR_KINDS = ("heading", "link", "form_field", "landmark", "button", "list_item")


class Action(BaseModel):
    """One proposed action. Validated before it reaches the gate."""

    tool: Tool
    key: str | None = None
    text: str | None = None
    ref: str | None = Field(None, description="Element id from the current observation")
    to_ref: str | None = None
    x: float | None = None
    y: float | None = None
    dx: float | None = None
    dy: float | None = None
    kind: str | None = None
    url: str | None = None
    answer: str | None = None
    reason: str | None = None
    rationale: str = Field("", description="Why the agent chose this; used by soft rules only")

    @property
    def group(self) -> ToolGroup:
        return TOOL_GROUPS[self.tool]

    @model_validator(mode="after")
    def _check_args(self) -> "Action":
        missing = [name for name in REQUIRED_ARGS.get(self.tool, ()) if getattr(self, name) is None]
        if missing:
            raise ValueError(f"{self.tool} needs {', '.join(missing)}")
        if self.tool in (Tool.SR_NEXT, Tool.SR_PREV) and self.kind not in SR_KINDS:
            raise ValueError(f"kind must be one of {', '.join(SR_KINDS)}")
        return self

    def free_text(self) -> str:
        """Everything the agent wrote in this action, for honeytoken and soft-rule checks."""
        parts = [self.text, self.answer, self.reason, self.url, self.rationale]
        return "\n".join(part for part in parts if part)
