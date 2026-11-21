"""Run and batch metrics, and the script that regenerates the results tables.

Proposed owner: Ibrahim (see Vanguard.md, team split).

Per run (docs/leakage-spec.md, Section 6): executed and attempted leakage rate per
limit (leaking steps / steps), any-leak flag, task success, steps, stuck, gate blocks,
latency per step (p50, p95) and per run, tokens and cost.

Per batch, grouped by persona x task x enforcement option x provider: means and spread
over repeated runs. Diversity (edit distance between action-type sequences) is A4.

All numbers are computed here, by code. The explanation generator may describe them
but never produces or changes a number.
"""

from dataclasses import dataclass

from vanguard.contracts import RunSummary, StepRecord


@dataclass
class RunMetrics:
    run_id: str
    success: bool
    steps: int
    blocked: int
    attempted_leak_rate: float
    executed_leak_rate: float
    latency_p50_ms: float
    latency_p95_ms: float
    input_tokens: int
    output_tokens: int
    cost_usd: float


def run_metrics(summary: RunSummary, steps: list[StepRecord]) -> RunMetrics:
    raise NotImplementedError("Metrics: see the module docstring")
