"""An offline provider for tests and rehearsals. Its output is never a result."""

from vanguard.contracts import Action

from .base import JsonReply, ModelReply, ModelRequest


class ScriptedProvider:
    """Replays a fixed list of actions, then gives up. A list inside the script is one
    call that returns several actions."""

    name = "fake"

    def __init__(
        self, script: list[Action | list[Action]] | None = None, json_replies: list | None = None
    ):
        self.script = list(script or [])
        self.json_replies = list(json_replies or [])
        self.calls = 0

    async def generate_json(self, system: str, user: str, schema: dict) -> JsonReply:
        """Replays prepared JSON answers; with none left, answers nothing usable."""
        self.calls += 1
        if self.json_replies:
            return JsonReply(value=self.json_replies.pop(0), model="scripted")
        return JsonReply(value=None, model="scripted", error="no scripted reply")

    async def next_action(self, request: ModelRequest) -> ModelReply:
        self.calls += 1
        if self.script:
            item = self.script.pop(0)
            actions = list(item) if isinstance(item, list) else [item]
        else:
            actions = [Action(tool="give_up", reason="script finished", rationale="no more steps")]
        actions = actions[: max(1, request.max_actions)]
        return ModelReply(
            action=actions[0], actions=actions, model="scripted", raw={"call": self.calls}
        )
