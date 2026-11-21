"""An offline provider for tests and rehearsals. Its output is never a result."""

from vanguard.contracts import Action

from .base import ModelReply, ModelRequest


class ScriptedProvider:
    """Replays a fixed list of actions, then gives up."""

    name = "fake"

    def __init__(self, script: list[Action] | None = None):
        self.script = list(script or [])
        self.calls = 0

    async def next_action(self, request: ModelRequest) -> ModelReply:
        self.calls += 1
        if self.script:
            action = self.script.pop(0)
        else:
            action = Action(tool="give_up", reason="script finished", rationale="no more steps")
        return ModelReply(action=action, model="scripted", raw={"call": self.calls})
