"""Failure analysis: tag every unsuccessful or leaking run with its causes, by code.

A3 asks for at least ten failures grouped by cause. The tags below are computed from
the stored records only, so they can be regenerated and checked. Each run gets all the
tags that apply and one primary cause (the first in CAUSES order). People then read a
sample of each group to write the qualitative analysis; the tags only do the grouping.
"""

from collections import Counter
from dataclasses import dataclass, field

from vanguard.checker import RunLeakage
from vanguard.contracts import RunOutcome, RunSummary, StepRecord

REFUSAL_LOOP = 3  # this many refused proposals in a row

# Ordered by how directly each explains the failure.
CAUSES: dict[str, str] = {
    "model_unavailable": "The model could not be reached (quota, key or network)",
    "executor_error": "The run crashed in the browser or the backend",
    "persona_leak": "The persona broke one of its own limits in an executed step",
    "invalid_output": "The model returned something that was not a valid action",
    "refusal_loop": "The agent kept proposing actions the gate refused",
    "action_errors": "Actions failed in the page (missing element, timeout)",
    "stuck": "Nothing changed for several steps",
    "step_limit": "The step limit ran out",
    "gave_up": "The agent gave up",
    "wrong_answer": "The agent said it was done, but the success check failed",
}


@dataclass
class RunFailure:
    run_id: str
    label: str
    outcome: str | None
    primary: str | None
    tags: list[str] = field(default_factory=list)
    detail: str = ""


def _longest_refusal_run(steps: list[StepRecord]) -> int:
    best = current = 0
    for step in steps:
        refused = step.proposed is not None and not step.gate.allowed
        current = current + 1 if refused else 0
        best = max(best, current)
    return best


def classify(summary: RunSummary, steps: list[StepRecord], leakage: RunLeakage) -> RunFailure:
    tags: list[str] = []
    detail = ""
    error = summary.error or ""
    if summary.outcome is RunOutcome.ERROR:
        tags.append(
            "model_unavailable" if error.startswith("model unavailable") else "executor_error"
        )
        detail = error
    if leakage.executed_steps:
        tags.append("persona_leak")
    if any(step.proposed is None for step in steps):
        tags.append("invalid_output")
    if _longest_refusal_run(steps) >= REFUSAL_LOOP:
        tags.append("refusal_loop")
    if any(step.execution_error for step in steps):
        tags.append("action_errors")
        detail = detail or next(s.execution_error for s in steps if s.execution_error) or ""
    if summary.outcome is RunOutcome.STUCK:
        tags.append("stuck")
    if summary.outcome is RunOutcome.STEP_LIMIT:
        tags.append("step_limit")
    if summary.outcome is RunOutcome.GAVE_UP:
        last = steps[-1].proposed if steps else None
        if last is not None and last.tool == "done":
            tags.append("wrong_answer")
            detail = detail or f"answer: {last.answer}"
        else:
            tags.append("gave_up")
            detail = detail or (last.reason if last and last.reason else "")
    primary = next((cause for cause in CAUSES if cause in tags), None)
    return RunFailure(
        run_id=summary.id,
        label=summary.config.label(),
        outcome=summary.outcome.value if summary.outcome else None,
        primary=primary,
        tags=tags,
        detail=(detail or "")[:300],
    )


def is_failure(item: RunFailure) -> bool:
    return item.outcome != RunOutcome.SUCCESS.value or "persona_leak" in item.tags


def group(items: list[RunFailure]) -> list[tuple[str, str, int, list[RunFailure]]]:
    """(cause, description, count, runs) for each primary cause, most common first."""
    failures = [item for item in items if is_failure(item) and item.primary]
    counts = Counter(item.primary for item in failures)
    return [
        (cause, CAUSES[cause], count, [i for i in failures if i.primary == cause])
        for cause, count in counts.most_common()
    ]


def markdown(items: list[RunFailure], examples: int = 3) -> str:
    groups = group(items)
    total = sum(count for _, _, count, _ in groups)
    lines = [
        f"{total} failing runs (unsuccessful, or with an executed limit break).",
        "",
        "| primary cause | runs | meaning | examples |",
        "|---|---|---|---|",
    ]
    for cause, meaning, count, runs in groups:
        shown = "; ".join(f"`{r.run_id[:8]}` {r.label}" for r in runs[:examples])
        lines.append(f"| {cause} | {count} | {meaning} | {shown} |")
    return "\n".join(lines)
