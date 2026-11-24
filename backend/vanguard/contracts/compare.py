"""Comparison of two batches: did a change (a site version, a method, a prompt) help?"""

from enum import StrEnum

from pydantic import BaseModel, Field


class CompareMatch(StrEnum):
    # Groups match on persona/task/enforcement/provider: the same setup, before and after.
    FULL = "full"
    # Groups match on persona/task only: for comparing methods or providers.
    PERSONA_TASK = "persona_task"


class Verdict(StrEnum):
    BETTER = "better"
    WORSE = "worse"
    SAME = "same"
    # The group is only in one of the two batches.
    ONLY_BASELINE = "only_baseline"
    ONLY_CANDIDATE = "only_candidate"


class GroupSnapshot(BaseModel):
    """Headline metrics of one group in one batch."""

    runs: int
    success_rate: float
    any_leak_rate: float
    mean_steps: float
    stuck_rate: float
    mean_blocked: float
    mean_cost_usd: float
    mean_repeated_attempts: float = 0.0
    mean_model_calls: float = 0.0
    failures: int = Field(description="Runs that failed or leaked (vanguard.failures)")


class MetricChange(BaseModel):
    metric: str
    baseline: float
    candidate: float
    delta: float = Field(description="candidate minus baseline")
    verdict: Verdict


class CompareGroup(BaseModel):
    key: str
    baseline: GroupSnapshot | None
    candidate: GroupSnapshot | None
    changes: list[MetricChange] = Field(default_factory=list)
    verdict: Verdict = Field(
        description="Worse if any headline metric got worse, else better or same"
    )


class FailureChange(BaseModel):
    """A failure cause that appears in only one of the two batches, for one group."""

    key: str
    cause: str
    meaning: str
    run_ids: list[str] = Field(description="Runs with this cause, in the batch where it appears")


class Comparison(BaseModel):
    baseline: str
    candidate: str
    match: CompareMatch
    groups: list[CompareGroup]
    new_failures: list[FailureChange] = Field(
        description="Causes in the candidate, not the baseline"
    )
    resolved_failures: list[FailureChange] = Field(
        description="Causes in the baseline, gone from the candidate"
    )
