import pytest
from test_agent_loop import KEYS, run, store  # noqa: F401  (fixture)

from vanguard import catalog
from vanguard.checker import check_run
from vanguard.contracts import Action, EnforcementOption
from vanguard.metrics import group_metrics, percentile, run_metrics

START = "http://localhost:3100/"
keyboard = catalog.persona("keyboard-only")
click = Action(tool="click", ref="e0", rationale="shortcut")


def test_percentile():
    assert percentile([], 50) == 0.0
    assert percentile([5], 95) == 5
    assert percentile([1, 2, 3, 4], 50) == pytest.approx(2.5)
    assert percentile([0, 10], 95) == pytest.approx(9.5)


def _metrics(store, enforcement, script, **prices):  # noqa: F811
    summary = run(store, "keyboard-only", enforcement, script)
    summary = store.get_run(summary.id)
    steps = store.steps(summary.id)
    return summary, run_metrics(summary, steps, check_run(steps, keyboard, START), **prices), steps


def test_run_metrics_prompt_only_vs_gate(store):  # noqa: F811
    _, loose, _ = _metrics(store, [EnforcementOption.PROMPT_ONLY], [click, *KEYS])
    _, strict, _ = _metrics(store, [EnforcementOption.GATE], [click, *KEYS])
    assert loose.executed_leak_steps == 1 and loose.any_executed_leak
    assert loose.pointer_evidence_steps == 1
    assert strict.executed_leak_steps == 0 and strict.attempted_leak_steps == 1
    assert strict.blocked == 1 and strict.success
    assert strict.executed_leak_rate == 0.0
    assert strict.attempted_leak_rate == pytest.approx(1 / strict.steps)


def test_cost_uses_configured_price(store):  # noqa: F811
    _, metrics, _ = _metrics(
        store, [EnforcementOption.GATE], KEYS, price_in_per_mtok=1.0, price_out_per_mtok=2.0
    )
    expected = (metrics.input_tokens * 1.0 + metrics.output_tokens * 2.0) / 1_000_000
    assert metrics.cost_usd == pytest.approx(expected)


def test_group_metrics(store):  # noqa: F811
    runs = [_metrics(store, [EnforcementOption.GATE], [click, *KEYS]) for _ in range(3)]
    runs += [_metrics(store, [EnforcementOption.PROMPT_ONLY], [click, *KEYS]) for _ in range(2)]
    groups = {g.key: g for g in group_metrics([(s, m, st) for s, m, st in runs])}
    gate = groups["keyboard-only/buy-one/gate/fake"]
    loose = groups["keyboard-only/buy-one/prompt_only/fake"]
    assert gate.runs == 3 and gate.success_rate == 1.0 and gate.any_leak_rate == 0.0
    assert loose.runs == 2 and loose.any_leak_rate == 1.0
    assert 0 <= gate.success_ci[0] <= 1.0 == gate.success_ci[1]
