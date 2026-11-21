"""Batch requests: many runs over persona x task x enforcement groups, repeated."""

from pydantic import BaseModel, Field

from .runs import Condition, EnforcementOption


class BatchRequest(BaseModel):
    batch_id: str | None = Field(
        None, description="Reuse an id to continue a stopped batch; a new id is made otherwise"
    )
    site_id: str
    task_ids: list[str] = Field(min_length=1)
    persona_ids: list[str] = Field(min_length=1)
    enforcements: list[list[EnforcementOption]] = Field(
        default_factory=lambda: [[EnforcementOption.PROMPT_ONLY], [EnforcementOption.GATE]],
        description="Each entry is one enforcement configuration, e.g. [prompt_only] or [gate]",
    )
    conditions: list[Condition] = Field(default_factory=list)
    provider: str = "gemini"
    repeats: int = Field(3, ge=1, le=50)
    max_steps: int | None = None
    seed: int = 0


class BatchGroup(BaseModel):
    task_id: str
    persona_id: str
    enforcement: list[EnforcementOption]
    target: int
    done: int


class BatchStatus(BaseModel):
    batch_id: str
    groups: list[BatchGroup]
    remaining: int
    stopped: str | None = Field(None, description="Why the batch stopped early, if it did")
