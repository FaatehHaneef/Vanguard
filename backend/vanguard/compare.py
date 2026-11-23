"""Compare two batches group by group: what got better, what got worse, which failures
are new and which are gone. Used by GET /compare and the web app's compare page.

A group is persona/task/enforcement/provider (match=full) or persona/task
(match=persona_task, for comparing methods or providers). Every number comes from the
stored records, scored the same way as the batch metrics.
"""

from collections import defaultdict

from vanguard import failures, results
from vanguard.contracts import RunStatus, RunSummary
from vanguard.contracts.compare import (
    CompareGroup,
    CompareMatch,
    Comparison,
    FailureChange,
    GroupSnapshot,
    MetricChange,
    Verdict,
)
from vanguard.metrics import RunMetrics, group_key
from vanguard.settings import Settings
from vanguard.store import RunStore

# Headline metrics and whether a higher value is better. mean_blocked is shown but has
# no direction: more refusals can mean a stricter gate or a worse agent.
DIRECTION: dict[str, bool] = {
    "success_rate": True,
    "any_leak_rate": False,
    "mean_steps": False,
    "stuck_rate": False,
    "mean_cost_usd": False,
}
TOLERANCE = 1e-9

Scored = tuple[RunSummary, RunMetrics, failures.RunFailure]


def key_for(summary: RunSummary, match: CompareMatch) -> str:
    if match is CompareMatch.PERSONA_TASK:
        return f"{summary.config.persona_id}/{summary.config.task_id}"
    return group_key(summary)


def _scored(store: RunStore, batch_id: str, settings: Settings) -> list[Scored]:
    out = []
    for summary in store.list_runs(batch_id, limit=10_000):
        if summary.status is not RunStatus.FINISHED:
            continue
        steps = store.steps(summary.id)
        leakage, metrics = results.score(summary, steps, settings)
        out.append((summary, metrics, failures.classify(summary, steps, leakage)))
    return out


def snapshot(members: list[Scored]) -> GroupSnapshot:
    n = len(members)
    metrics = [m for _, m, _ in members]
    return GroupSnapshot(
        runs=n,
        success_rate=sum(m.success for m in metrics) / n,
        any_leak_rate=sum(m.any_executed_leak for m in metrics) / n,
        mean_steps=sum(m.steps for m in metrics) / n,
        stuck_rate=sum(m.stuck for m in metrics) / n,
        mean_blocked=sum(m.blocked for m in metrics) / n,
        mean_cost_usd=sum(m.cost_usd for m in metrics) / n,
        failures=sum(failures.is_failure(f) for _, _, f in members),
    )


def _verdict(metric: str, delta: float) -> Verdict:
    if abs(delta) <= TOLERANCE or metric not in DIRECTION:
        return Verdict.SAME
    return Verdict.BETTER if (delta > 0) == DIRECTION[metric] else Verdict.WORSE


def compare_group(key: str, base: GroupSnapshot | None, cand: GroupSnapshot | None) -> CompareGroup:
    if base is None or cand is None:
        only = Verdict.ONLY_CANDIDATE if base is None else Verdict.ONLY_BASELINE
        return CompareGroup(key=key, baseline=base, candidate=cand, verdict=only)
    changes = []
    for metric in (*DIRECTION, "mean_blocked"):
        before, after = getattr(base, metric), getattr(cand, metric)
        delta = after - before
        changes.append(
            MetricChange(
                metric=metric,
                baseline=before,
                candidate=after,
                delta=delta,
                verdict=_verdict(metric, delta),
            )
        )
    verdicts = {change.verdict for change in changes}
    overall = (
        Verdict.WORSE
        if Verdict.WORSE in verdicts
        else Verdict.BETTER
        if Verdict.BETTER in verdicts
        else Verdict.SAME
    )
    return CompareGroup(key=key, baseline=base, candidate=cand, changes=changes, verdict=overall)


def _causes(members: list[Scored]) -> dict[str, list[str]]:
    """Primary failure cause -> run ids, for the failing runs in one group."""
    found: dict[str, list[str]] = defaultdict(list)
    for summary, _, failure in members:
        if failures.is_failure(failure) and failure.primary:
            found[failure.primary].append(summary.id)
    return found


def _failure_changes(
    keys: list[str], here: dict[str, list[Scored]], there: dict[str, list[Scored]]
) -> list[FailureChange]:
    """Causes found in `here` for a group whose `there` side does not have them."""
    out = []
    for key in keys:
        if key not in here or key not in there:
            continue  # a group in one batch only has nothing to compare against
        other = _causes(there[key])
        for cause, run_ids in sorted(_causes(here[key]).items()):
            if cause not in other:
                out.append(
                    FailureChange(
                        key=key, cause=cause, meaning=failures.CAUSES[cause], run_ids=run_ids
                    )
                )
    return out


def compare(
    store: RunStore,
    baseline: str,
    candidate: str,
    settings: Settings,
    match: CompareMatch = CompareMatch.FULL,
) -> Comparison:
    sides: list[dict[str, list[Scored]]] = []
    for batch_id in (baseline, candidate):
        grouped: dict[str, list[Scored]] = defaultdict(list)
        for item in _scored(store, batch_id, settings):
            grouped[key_for(item[0], match)].append(item)
        sides.append(grouped)
    base, cand = sides
    keys = sorted(base.keys() | cand.keys())
    groups = [
        compare_group(
            key,
            snapshot(base[key]) if key in base else None,
            snapshot(cand[key]) if key in cand else None,
        )
        for key in keys
    ]
    return Comparison(
        baseline=baseline,
        candidate=candidate,
        match=match,
        groups=groups,
        new_failures=_failure_changes(keys, cand, base),
        resolved_failures=_failure_changes(keys, base, cand),
    )
