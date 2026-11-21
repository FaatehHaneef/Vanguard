"""Step records: everything the checker and the labellers need about one step."""

from datetime import datetime

from pydantic import BaseModel, Field

from .actions import Action
from .persona import PerceptionMode


class Rect(BaseModel):
    x: float
    y: float
    width: float
    height: float

    def intersects(self, other: "Rect") -> bool:
        return (
            self.x < other.x + other.width
            and other.x < self.x + self.width
            and self.y < other.y + other.height
            and other.y < self.y + self.height
        )


class Observation(BaseModel):
    """What the persona was shown before choosing this step."""

    mode: PerceptionMode
    url: str
    content: str = Field(description="Text given to the model (DOM summary, ARIA snapshot, ...)")
    links: list[str] = Field(default_factory=list, description="Link targets visible in this view")
    window: Rect | None = Field(None, description="Magnified window, for L3")
    screenshot_path: str | None = None


class GateDecision(BaseModel):
    allowed: bool
    rule: str | None = Field(None, description="Rule id that blocked the action, e.g. 'H1'")
    message: str | None = Field(None, description="What the agent is told when blocked")


class BrowserEvent(BaseModel):
    """A low-level input event recorded in the page during the step."""

    type: str  # keydown, pointerdown, mousedown, wheel, focusin, ...
    trusted: bool
    target: str | None = None
    t_ms: float = 0


class StepRecord(BaseModel):
    run_id: str
    index: int
    started_at: datetime
    observation: Observation
    proposed: Action | None = Field(None, description="None when the model output was unusable")
    model_error: str | None = None
    gate: GateDecision
    verifier: GateDecision | None = Field(
        None, description="The verifier agent's decision (option 4), when it ran"
    )
    executed: bool
    execution_error: str | None = None
    events: list[BrowserEvent] = Field(default_factory=list)
    url_after: str | None = None
    focus_after: str | None = None
    target_box: Rect | None = None
    latency_ms: float = 0
    input_tokens: int = 0
    output_tokens: int = 0
    cost_usd: float = 0
