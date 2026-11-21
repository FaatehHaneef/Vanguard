"""The model-provider interface.

Every step is one self-contained request: a system prompt and a user message that
already contain the persona, the task, a short history and the current observation.
There is no growing chat history, so context stays bounded and every provider
(Gemini, a local model, Groq, OpenAI) is called the same way.

The provider must answer with exactly one tool call. The tool names and argument
schemas come from vanguard.providers.tools.
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


@dataclass
class ModelReply:
    action: Action | None  # None when the reply could not be turned into a valid Action
    model: str
    raw: dict = field(default_factory=dict)
    error: str | None = None
    latency_ms: float = 0
    input_tokens: int = 0
    output_tokens: int = 0


class Provider(Protocol):
    name: str

    async def next_action(self, request: ModelRequest) -> ModelReply: ...
