"""The model-provider interface.

Every step is one self-contained request: a system prompt and a user message that
already contain the persona, the task, a short history and the current observation.
There is no growing chat history, so context stays bounded and every provider
(Gemini, a local model, Groq, OpenAI) is called the same way.

The provider answers with one or more tool calls, in order (at most
ModelRequest.max_actions). The tool names and argument schemas come from
vanguard.providers.tools.
"""

from dataclasses import dataclass, field
from typing import Protocol

from vanguard.contracts import Action


class ProviderUnavailable(RuntimeError):
    """No key, quota exhausted, or the service did not answer. Callers record and stop."""


@dataclass
class ModelRequest:
    system: str
    user: str
    tool_names: list[str]  # tools offered this step
    seed: int = 0
    max_actions: int = 1  # most tool calls used from the reply


@dataclass
class ModelReply:
    action: Action | None  # None when the reply could not be turned into a valid Action
    model: str
    # Every usable action of the reply in order, starting with `action`. Parsing stops at
    # the first unusable tool call, so a bad later call never hides a good first one.
    actions: list[Action] = field(default_factory=list)
    raw: dict = field(default_factory=dict)
    error: str | None = None
    latency_ms: float = 0
    input_tokens: int = 0
    output_tokens: int = 0


@dataclass
class JsonReply:
    """A structured (non-action) answer, used by the explanation generator."""

    value: dict | None
    model: str
    error: str | None = None
    latency_ms: float = 0
    input_tokens: int = 0
    output_tokens: int = 0


def parse_calls(calls: list[tuple[str, dict]], max_actions: int) -> tuple[list[Action], str | None]:
    """Turn (name, args) tool calls into actions, up to max_actions, stopping at the
    first one that is not a valid action. The error is set only when the first fails."""
    from .tools import to_action

    actions: list[Action] = []
    for name, args in calls[: max(1, max_actions)]:
        action, problem = to_action(name, args)
        if action is None:
            return actions, (problem if not actions else None)
        actions.append(action)
    return actions, None


class Provider(Protocol):
    name: str

    async def next_action(self, request: ModelRequest) -> ModelReply: ...

    async def generate_json(self, system: str, user: str, schema: dict) -> JsonReply: ...
