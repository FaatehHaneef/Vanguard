"""Task-level scoring: whole tasks, per task and per scenario, over repeated runs.

    python -m vanguard.evaluation task-report --batches <ids...> [--out <file>]

A row is one task (or one scenario) for one persona under one enforcement option, over
all its finished runs in the given batches. For each row:
  - completion rate: runs that reached the task's success check, with a 95% Wilson interval;
  - mean actions and mean model calls per run (several actions can share one call);
  - mean repeated attempts per run (vanguard.metrics.repetition);
  - mean refusals per run: actions the gate refused;
  - stuck rate and step-limit rate: the share of runs that ended that way;
  - task time p50 and p95: the run's total latency (model and browser time), over runs;
  - mean cost per run;
  - failure causes: the primary cause (vanguard.failures) of each failed run, counted.
"""

import argparse
from collections import Counter, defaultdict
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime

from vanguard.contracts import RunOutcome
from vanguard.failures import CAUSES, is_failure
from vanguard.metrics import percentile
from vanguard.metrics.stats import wilson_interval

from .commands import Command, register
from .data import ScoredRun, add_batch_arguments, load_runs, open_store, write


@dataclass
class TaskRow:
    key: str  # task or scenario
    persona_id: str
    enforcement: str
    runs: int
    completion_rate: float
    completion_ci: tuple[float, float]
    mean_actions: float
    mean_model_calls: float
    mean_repeated_attempts: float
    mean_refusals: float
    stuck_rate: float
    step_limit_rate: float
    time_p50_ms: float
    time_p95_ms: float
    mean_cost_usd: float
    failure_causes: Counter = field(default_factory=Counter)


def _row(key: str, persona_id: str, enforcement: str, runs: list[ScoredRun]) -> TaskRow:
    n = len(runs)
    wins = sum(run.metrics.success for run in runs)
    times = [run.metrics.latency_total_ms for run in runs]
    causes = Counter(
        run.failure.primary for run in runs if is_failure(run.failure) and run.failure.primary
    )
    return TaskRow(
        key=key,
        persona_id=persona_id,
        enforcement=enforcement,
        runs=n,
        completion_rate=wins / n,
        completion_ci=wilson_interval(wins, n),
        mean_actions=sum(run.metrics.actions for run in runs) / n,
        mean_model_calls=sum(run.metrics.model_calls for run in runs) / n,
        mean_repeated_attempts=sum(run.metrics.repeated_attempts for run in runs) / n,
        mean_refusals=sum(run.metrics.blocked for run in runs) / n,
        stuck_rate=sum(run.summary.outcome is RunOutcome.STUCK for run in runs) / n,
        step_limit_rate=sum(run.summary.outcome is RunOutcome.STEP_LIMIT for run in runs) / n,
        time_p50_ms=percentile(times, 50),
        time_p95_ms=percentile(times, 95),
        mean_cost_usd=sum(run.metrics.cost_usd for run in runs) / n,
        failure_causes=causes,
    )


def task_rows(runs: list[ScoredRun], by: Callable[[ScoredRun], str]) -> list[TaskRow]:
    """One row per (by(run), persona, enforcement), sorted."""
    groups: dict[tuple[str, str, str], list[ScoredRun]] = defaultdict(list)
    for run in runs:
        groups[(by(run), run.persona_id, run.enforcement)].append(run)
    return [_row(*key, members) for key, members in sorted(groups.items())]


def by_task(runs: list[ScoredRun]) -> list[TaskRow]:
    return task_rows(runs, lambda run: run.task_id)


def by_scenario(runs: list[ScoredRun]) -> list[TaskRow]:
    return task_rows(runs, lambda run: run.scenario)


def _causes(row: TaskRow) -> str:
    return ", ".join(f"{cause} {count}" for cause, count in row.failure_causes.most_common()) or "-"


def table(rows: list[TaskRow], first: str) -> str:
    head = (
        f"| {first} | persona | enforcement | runs | completion [95% CI] | actions | calls "
        "| repeats | refusals | stuck | step limit | time p50 | time p95 | cost | failure causes |"
    )
    lines = [head, "|" + "---|" * 15]
    for row in rows:
        low, high = row.completion_ci
        lines.append(
            f"| `{row.key}` | {row.persona_id} | {row.enforcement} | {row.runs} "
            f"| {row.completion_rate:.0%} [{low:.0%}-{high:.0%}] | {row.mean_actions:.1f} "
            f"| {row.mean_model_calls:.1f} | {row.mean_repeated_attempts:.1f} "
            f"| {row.mean_refusals:.1f} | {row.stuck_rate:.0%} | {row.step_limit_rate:.0%} "
            f"| {row.time_p50_ms / 1000:.1f} s | {row.time_p95_ms / 1000:.1f} s "
            f"| ${row.mean_cost_usd:.4f} | {_causes(row)} |"
        )
    return "\n".join(lines)


def report(runs: list[ScoredRun], batch_ids: list[str], now: datetime | None = None) -> str:
    when = (now or datetime.now(UTC)).strftime("%Y-%m-%d %H:%M UTC")
    used = sorted({cause for run in runs for cause in [run.failure.primary] if cause})
    parts = [
        "# Task-level results",
        "",
        f"Generated by `python -m vanguard.evaluation task-report` on {when} "
        f"from {len(runs)} finished runs in batches {', '.join(f'`{b}`' for b in batch_ids)}.",
        "",
        "A row is one task (or scenario) for one persona under one enforcement option. "
        "Completion is the share of runs that passed the task's success check, with a 95% "
        "Wilson interval. Actions, calls, repeats (repeated attempts) and refusals are means "
        "per run. Stuck and step limit are shares of runs. Time is the run's total latency, "
        "over runs. Failure causes count each failed run's primary cause.",
        "",
    ]
    if not runs:
        parts.append("No finished runs in these batches.")
        return "\n".join(parts) + "\n"
    parts += ["## By task", "", table(by_task(runs), "task"), ""]
    parts += ["## By scenario", "", table(by_scenario(runs), "scenario"), ""]
    if used:
        parts += ["## Failure causes", ""]
        parts += [f"- `{cause}`: {CAUSES[cause]}" for cause in used]
        parts.append("")
    return "\n".join(parts)


def _add_arguments(parser: argparse.ArgumentParser) -> None:
    add_batch_arguments(parser, "task-level.md")


def _run(args: argparse.Namespace) -> int:
    store, settings = open_store()
    runs = load_runs(store, args.batches, settings)
    write(args.out, report(runs, args.batches))
    return 0


register(
    Command(
        "task-report",
        "Score runs as whole tasks, per task and per scenario.",
        _add_arguments,
        _run,
    )
)
