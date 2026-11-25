"""Loading and scoring stored runs for the evaluation commands.

Every evaluation command reads the same thing: the finished runs of some batches, each
scored by the checker and the metrics exactly as vanguard.results scores them, with its
failure cause from vanguard.failures.
"""

import argparse
from dataclasses import dataclass
from pathlib import Path

from vanguard import catalog, failures, results
from vanguard.checker import RunLeakage
from vanguard.contracts import RunStatus, RunSummary, StepRecord
from vanguard.metrics import RunMetrics
from vanguard.settings import REPO_ROOT, Settings, get_settings
from vanguard.store import RunStore

RESULTS_DIR = REPO_ROOT / "docs" / "results"


@dataclass
class ScoredRun:
    summary: RunSummary
    steps: list[StepRecord]
    leakage: RunLeakage
    metrics: RunMetrics
    failure: failures.RunFailure

    @property
    def persona_id(self) -> str:
        return self.summary.config.persona_id

    @property
    def task_id(self) -> str:
        return self.summary.config.task_id

    @property
    def enforcement(self) -> str:
        return "+".join(option.value for option in self.summary.config.enforcement)

    @property
    def scenario(self) -> str:
        try:
            return str(catalog.task(self.task_id).scenario)
        except LookupError:
            return "unknown"


def score_run(summary: RunSummary, steps: list[StepRecord], settings: Settings) -> ScoredRun:
    leakage, metrics = results.score(summary, steps, settings)
    return ScoredRun(summary, steps, leakage, metrics, failures.classify(summary, steps, leakage))


def load_runs(store: RunStore, batch_ids: list[str], settings: Settings) -> list[ScoredRun]:
    """The finished runs of these batches, scored, in creation order, each once."""
    seen: set[str] = set()
    runs: list[ScoredRun] = []
    for batch_id in batch_ids:
        for summary in store.list_runs(batch_id, limit=100_000):
            if summary.status is not RunStatus.FINISHED or summary.id in seen:
                continue
            seen.add(summary.id)
            runs.append(score_run(summary, store.steps(summary.id), settings))
    runs.sort(key=lambda run: run.summary.created_at)
    return runs


def add_batch_arguments(parser: argparse.ArgumentParser, default_out: str) -> None:
    parser.add_argument("--batches", nargs="+", required=True, metavar="ID", help="batch ids")
    parser.add_argument(
        "--out",
        type=Path,
        default=RESULTS_DIR / default_out,
        help=f"Markdown file to write (default docs/results/{default_out})",
    )


def open_store() -> tuple[RunStore, Settings]:
    settings = get_settings()
    store = RunStore(settings.database_url)
    store.create_schema()
    return store, settings


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")
    print(f"wrote {path}")
