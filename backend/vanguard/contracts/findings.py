"""Audit findings: usability problems found in runs, and why each failure happened."""

from enum import StrEnum

from pydantic import BaseModel, Field

# Shown on every findings report (instructor's point 17).
LIMITS_STATEMENT = (
    "Simulated users cannot establish accessibility compliance, and they do not represent "
    "the experience of real people with disabilities. Findings marked as a barrier for a "
    "limit are candidates for evaluation by people; findings attributed to the agent are "
    "failures of the simulated user itself, not of the website."
)


class FindingKind(StrEnum):
    INACCESSIBLE_CONTROL = "inaccessible_control"  # a control the persona could not use
    NAVIGATION_FAILURE = "navigation_failure"  # failed actions, refused routes, stuck runs
    REPEATED_ACTIONS = "repeated_actions"  # the same action again without any change
    CONFUSING_WORKFLOW = "confusing_workflow"  # far longer than the control, or going round
    FAILED_TASK = "failed_task"  # the task was not completed


class Attribution(StrEnum):
    """Where a failure comes from (instructor's point 9)."""

    # The control (unrestricted) agent fails the same task too: the interface or the
    # task is a problem for everyone.
    SITE = "site"
    # The control succeeds; this persona fails while running into its own limit (refused
    # actions, a planted barrier for that limit). A candidate accessibility barrier.
    RESTRICTION = "restriction"
    # The control succeeds; nothing about the persona's limits explains the failure:
    # the simulated user's own reasoning (wrong answer, giving up, going round).
    AGENT = "agent"
    # The model or the browser failed; nothing can be concluded from the run.
    INFRASTRUCTURE = "infrastructure"
    # No finished control run of the same task to compare with.
    UNKNOWN = "unknown"


class Finding(BaseModel):
    kind: FindingKind
    run_id: str
    steps: list[int] = Field(default_factory=list, description="Step indexes (0-based)")
    summary: str
    element: str | None = Field(None, description="The control, as the persona perceived it")
    url: str | None = None


class RunAttribution(BaseModel):
    run_id: str
    label: str
    outcome: str | None
    attribution: Attribution
    reason: str
    control_runs: int = Field(description="Finished control runs of the same task compared with")
    control_success_rate: float | None = None
    expected: str | None = Field(None, description="The site manifest's expected outcome")


class FindingsReport(BaseModel):
    scope: str = Field(description="What the report covers, e.g. a batch id or a run id")
    runs: int
    findings: list[Finding]
    attributions: list[RunAttribution] = Field(description="One per run that failed")
    counts: dict[str, int] = Field(description="Findings per kind")
    attribution_counts: dict[str, int] = Field(description="Failed runs per attribution")
    limits_statement: str = LIMITS_STATEMENT
