"""Tool declarations offered to the model, as JSON Schema.

All tools are offered to every persona, whatever its limits. A keyboard-only persona
is *told* it cannot use a mouse, but the pointer tools stay available: that is what
makes leakage observable. Enforcement is the gate's job, not the tool list's.
"""

from pydantic import ValidationError

from vanguard.contracts import Action, Tool
from vanguard.contracts.actions import SR_KINDS

_STRING = {"type": "string"}
_NUMBER = {"type": "number"}

TOOL_SPECS: dict[Tool, tuple[str, dict]] = {
    Tool.PRESS: ("Press a key, e.g. Tab, Shift+Tab, Enter, Space, ArrowDown, Escape.", {"key": _STRING}),
    Tool.TYPE: ("Type text into the element that currently has focus.", {"text": _STRING}),
    Tool.CLICK: ("Click an element by its id from the observation.", {"ref": _STRING}),
    Tool.CLICK_AT: ("Click at page coordinates.", {"x": _NUMBER, "y": _NUMBER}),
    Tool.HOVER: ("Move the mouse over an element.", {"ref": _STRING}),
    Tool.DRAG: ("Drag one element onto another.", {"ref": _STRING, "to_ref": _STRING}),
    Tool.WHEEL: ("Scroll with the mouse wheel.", {"dx": _NUMBER, "dy": _NUMBER}),
    Tool.SR_NEXT: (
        "Screen reader: move to the next element of a kind.",
        {"kind": {"type": "string", "enum": list(SR_KINDS)}},
    ),
    Tool.SR_PREV: (
        "Screen reader: move to the previous element of a kind.",
        {"kind": {"type": "string", "enum": list(SR_KINDS)}},
    ),
    Tool.SR_READ: ("Screen reader: read the current element again.", {}),
    Tool.SR_ACTIVATE: ("Screen reader: activate the current element.", {}),
    Tool.PAN: ("Magnifier: move the magnified view.", {"dx": _NUMBER, "dy": _NUMBER}),
    Tool.PAN_TO_FOCUS: ("Magnifier: move the view to the focused element.", {}),
    Tool.GOTO: ("Go to an address.", {"url": _STRING}),
    Tool.BACK: ("Go back one page.", {}),
    Tool.RELOAD: ("Reload the page.", {}),
    Tool.DONE: ("Finish: the task is complete. Give the answer if one was asked for.", {"answer": _STRING}),
    Tool.GIVE_UP: ("Stop: the task cannot be completed. Say why.", {"reason": _STRING}),
}

RATIONALE = {"type": "string", "description": "One short sentence: why this action."}


def json_schema(tool: Tool) -> dict:
    _, args = TOOL_SPECS[tool]
    properties = {**args, "rationale": RATIONALE}
    return {"type": "object", "properties": properties, "required": [*args, "rationale"]}


def description(tool: Tool) -> str:
    return TOOL_SPECS[tool][0]


def all_tool_names() -> list[str]:
    return [tool.value for tool in TOOL_SPECS]


def to_action(name: str, args: dict) -> tuple[Action | None, str | None]:
    """Turn a model's tool call into an Action, or explain why it could not."""
    try:
        return Action.model_validate({"tool": name, **(args or {})}), None
    except ValidationError as error:
        return None, f"invalid tool call {name}: {error.errors()[0]['msg']}"
