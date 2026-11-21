"""Scoring stored runs: checker + metrics, for the API, the CLI report and the tables.

Everything here is deterministic. A run is scored from its stored steps only, so the
numbers can be regenerated at any time from the database.
"""

from dataclasses import asdict

from vanguard import catalog, failures
from vanguard.checker import RunLeakage, check_run
from vanguard.contracts import RunStatus, RunSummary, StepRecord
from vanguard.metrics import GroupMetrics, RunMetrics, group_metrics, run_metrics
from vanguard.settings import Settings
from vanguard.store import RunStore


def start_url(summary: RunSummary) -> str:
    site = catalog.site(summary.config.site_id)
    return site.origin + catalog.task(summary.config.task_id).start_path


def score(
    summary: RunSummary, steps: list[StepRecord], settings: Settings
) -> tuple[RunLeakage, RunMetrics]:
    persona = catalog.persona(summary.config.persona_id)
    leakage = check_run(steps, persona, start_url(summary))
    metrics = run_metrics(
        summary,
        steps,
        leakage,
        price_in_per_mtok=settings.price_in_per_mtok,
        price_out_per_mtok=settings.price_out_per_mtok,
    )
    return leakage, metrics


def leakage_dict(leakage: RunLeakage) -> list[dict]:
    def violations(items):
        return [asdict(v) for v in items]

    return [
        {"index": s.index, "attempted": violations(s.attempted), "executed": violations(s.executed)}
        for s in leakage.steps
    ]


def run_report(store: RunStore, run_id: str, settings: Settings) -> dict | None:
    summary = store.get_run(run_id)
    if summary is None:
        return None
    steps = store.steps(run_id)
    leakage, metrics = score(summary, steps, settings)
    return {"run": summary, "metrics": metrics.as_dict(), "steps": leakage_dict(leakage)}


def batch_groups(store: RunStore, batch_id: str | None, settings: Settings) -> list[GroupMetrics]:
    scored = []
    for summary in store.list_runs(batch_id, limit=10_000):
        if summary.status is not RunStatus.FINISHED:
            continue
        steps = store.steps(summary.id)
        _, metrics = score(summary, steps, settings)
        scored.append((summary, metrics, steps))
    return group_metrics(scored)


COLUMNS = [
    ("group", lambda g: g.key),
    ("runs", lambda g: g.runs),
    ("success", lambda g: f"{g.success_rate:.0%} [{g.success_ci[0]:.0%}-{g.success_ci[1]:.0%}]"),
    (
        "any leak",
        lambda g: f"{g.any_leak_rate:.0%} [{g.any_leak_ci[0]:.0%}-{g.any_leak_ci[1]:.0%}]",
    ),
    ("attempted/step", lambda g: f"{g.mean_attempted_leak_rate:.2f}"),
    ("executed/step", lambda g: f"{g.mean_executed_leak_rate:.2f}"),
    ("steps", lambda g: f"{g.mean_steps:.1f}"),
    ("stuck", lambda g: f"{g.stuck_rate:.0%}"),
    ("blocked", lambda g: f"{g.mean_blocked:.1f}"),
    ("p50 ms", lambda g: f"{g.latency_p50_ms:.0f}"),
    ("p95 ms", lambda g: f"{g.latency_p95_ms:.0f}"),
    ("cost $", lambda g: f"{g.mean_cost_usd:.4f}"),
]


def markdown_table(groups: list[GroupMetrics]) -> str:
    header = "| " + " | ".join(name for name, _ in COLUMNS) + " |"
    rule = "|" + "|".join("---" for _ in COLUMNS) + "|"
    rows = ["| " + " | ".join(str(get(g)) for _, get in COLUMNS) + " |" for g in groups]
    note = "Rates with 95% Wilson intervals. Leakage is decided by code (vanguard.checker)."
    return "\n".join([header, rule, *rows, "", note])


def batch_failures(
    store: RunStore, batch_id: str | None, settings: Settings
) -> list[failures.RunFailure]:
    out = []
    for summary in store.list_runs(batch_id, limit=10_000):
        if summary.status not in (RunStatus.FINISHED, RunStatus.FAILED):
            continue
        steps = store.steps(summary.id)
        leakage, _ = score(summary, steps, settings)
        out.append(failures.classify(summary, steps, leakage))
    return out
