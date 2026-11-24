"""Run configuration and outcomes."""

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class EnforcementOption(StrEnum):
    PROMPT_ONLY = "prompt_only"  # option 1, the baseline
    GATE = "gate"  # option 2, code-enforced limits
    BOUNDED_PERCEPTION = "bounded_perception"  # option 3
    VERIFIER = "verifier"  # option 4, LLM verifier before execution
    FINETUNED = "finetuned"  # option 5 (planned, A4)


class Condition(StrEnum):
    MOBILE = "mobile"
    SLOW_NETWORK = "slow_network"


class RunStatus(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    FINISHED = "finished"
    FAILED = "failed"


class RunOutcome(StrEnum):
    SUCCESS = "success"
    GAVE_UP = "gave_up"
    STUCK = "stuck"
    STEP_LIMIT = "step_limit"
    ERROR = "error"


class RunConfig(BaseModel):
    site_id: str
    task_id: str
    persona_id: str
    enforcement: list[EnforcementOption] = Field(
        default_factory=lambda: [EnforcementOption.PROMPT_ONLY]
    )
    provider: str = "gemini"
    model: str | None = None
    perception_format: str = "dom_summary"  # alternative (b)
    conditions: list[Condition] = Field(default_factory=list)
    seed: int = 0
    repeat_index: int = 0
    max_steps: int | None = None
    actions_per_call: int | None = Field(
        None,
        ge=1,
        le=8,
        description="Most actions the model may return in one call; filled from the "
        "settings when a run is created. None in older runs, which used one.",
    )
    batch_id: str | None = None

    def label(self) -> str:
        options = "+".join(option.value for option in self.enforcement)
        return f"{self.persona_id}/{self.task_id}/{options}/{self.provider}#{self.repeat_index}"


class RunSummary(BaseModel):
    id: str
    config: RunConfig
    status: RunStatus
    outcome: RunOutcome | None = None
    steps: int = 0
    blocked: int = 0
    created_at: datetime
    finished_at: datetime | None = None
    error: str | None = None
