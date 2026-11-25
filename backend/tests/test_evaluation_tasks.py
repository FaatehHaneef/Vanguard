"""Task-level scoring (vanguard.evaluation.tasks) over scripted runs on the fake shop.

The helpers here (scripted_run, scored) are reused by the other evaluation tests.
"""

import asyncio

import pytest

from vanguard import catalog
from vanguard.agent import run_once
from vanguard.contracts import Action, EnforcementOption, RunConfig, RunOutcome
from vanguard.evaluation import data, tasks
from vanguard.evaluation.__main__ import main
from vanguard.executor import FakeExecutor
from vanguard.providers import ScriptedProvider
from vanguard.settings import Settings
from vanguard.store import RunStore

SITE = catalog.site("tallowmere")
tab = Action(tool="press", key="Tab")
enter = Action(tool="press", key="Enter")
escape = Action(tool="press", key="Escape")
click = Action(tool="click", ref="e0", rationale="shortcut")
KEYS = [tab, enter] * 4  # the fake shop's keyboard route to /thanks/
CHEAPEST = Action(tool="done", answer="Moss Path, $16.00", rationale="cheapest")
SETTINGS = Settings(_env_file=None)


@pytest.fixture
def store():
    store = RunStore("sqlite:///:memory:")
    store.create_schema()
    return store


def scripted_run(
    store,
    script,
    *,
    persona="keyboard-only",
    task="buy-one",
    batch="b1",
    enforcement=EnforcementOption.GATE,
    max_steps=20,
    stuck_after=5,
):
    config = RunConfig(
        site_id=SITE.id,
        task_id=task,
        persona_id=persona,
        enforcement=[enforcement],
        provider="fake",
        batch_id=batch,
        actions_per_call=1,
    )
    summary = store.create_run(config)
    asyncio.run(
        run_once(
            summary.id,
            config,
            catalog.persona(persona),
            SITE,
            catalog.task(task),
            ScriptedProvider(list(script)),
            FakeExecutor(),
            store,
            allowed_origins=[SITE.origin],
            max_steps=max_steps,
            stuck_after=stuck_after,
        )
    )
    return store.get_run(summary.id)


def scored(store, *batches):
    return data.load_runs(store, list(batches) or ["b1"], SETTINGS)


def test_load_runs_scores_finished_runs_once(store):
    scripted_run(store, KEYS, batch="b1")
    scripted_run(store, KEYS, batch="b2")
    runs = scored(store, "b1", "b2", "b1")
    assert len(runs) == 2
    assert all(run.metrics.success and run.scenario == "checkout" for run in runs)
    assert scored(store, "missing") == []


def test_completion_with_wilson_interval_per_task(store):
    for _ in range(3):
        scripted_run(store, KEYS)
    scripted_run(store, [escape, Action(tool="give_up", reason="lost")])
    (row,) = tasks.by_task(scored(store))
    assert (row.key, row.persona_id, row.enforcement, row.runs) == (
        "buy-one",
        "keyboard-only",
        "gate",
        4,
    )
    assert row.completion_rate == 0.75
    low, high = row.completion_ci
    assert 0.0 < low < 0.75 < high <= 1.0
    assert row.failure_causes == {"gave_up": 1}


def test_actions_calls_refusals_and_repeats(store):
    # Two refused clicks (the second repeats the first), then the keyboard route.
    scripted_run(store, [click, click, *KEYS])
    (row,) = tasks.by_task(scored(store))
    assert row.mean_actions == 10
    assert row.mean_model_calls == 10  # one action per call
    assert row.mean_refusals == 2
    assert row.mean_repeated_attempts == 1
    assert row.completion_rate == 1.0 and not row.failure_causes


def test_stuck_and_step_limit_rates(store):
    scripted_run(store, [escape] * 10, stuck_after=3)
    scripted_run(store, [tab] * 10, max_steps=4)
    scripted_run(store, KEYS)
    (row,) = tasks.by_task(scored(store))
    assert row.stuck_rate == pytest.approx(1 / 3)
    assert row.step_limit_rate == pytest.approx(1 / 3)
    assert row.failure_causes == {"stuck": 1, "step_limit": 1}


def test_rows_split_by_persona_and_scenario(store):
    scripted_run(store, KEYS, task="buy-one")
    scripted_run(store, [CHEAPEST], task="cheapest")
    scripted_run(store, [CHEAPEST], task="cheapest", persona="unrestricted")
    by_task = {(r.key, r.persona_id) for r in tasks.by_task(scored(store))}
    assert by_task == {
        ("buy-one", "keyboard-only"),
        ("cheapest", "keyboard-only"),
        ("cheapest", "unrestricted"),
    }
    by_scenario = {(r.key, r.persona_id): r for r in tasks.by_scenario(scored(store))}
    assert set(by_scenario) == {
        ("checkout", "keyboard-only"),
        ("information", "keyboard-only"),
        ("information", "unrestricted"),
    }
    assert by_scenario[("information", "unrestricted")].completion_rate == 1.0


def test_wrong_answer_is_a_failure_cause(store):
    scripted_run(store, [Action(tool="done", answer="Dusk Ember")], task="cheapest")
    (row,) = tasks.by_task(scored(store))
    assert row.completion_rate == 0.0
    assert row.failure_causes == {"wrong_answer": 1}
    assert store.list_runs("b1")[0].outcome is RunOutcome.GAVE_UP


def test_report_lists_both_tables_and_the_causes(store):
    scripted_run(store, KEYS)
    scripted_run(store, [escape, Action(tool="give_up", reason="lost")])
    text = tasks.report(scored(store), ["b1"])
    assert "## By task" in text and "## By scenario" in text
    assert "| `buy-one` | keyboard-only | gate | 2 | 50% [" in text
    assert "| `checkout` | keyboard-only | gate | 2 |" in text
    assert "gave_up 1" in text and "- `gave_up`: The agent gave up" in text
    assert "No finished runs" in tasks.report([], ["b1"])


def test_task_report_command_writes_the_file(store, tmp_path, monkeypatch):
    scripted_run(store, KEYS, batch="suite")
    monkeypatch.setattr("vanguard.evaluation.tasks.open_store", lambda: (store, SETTINGS))
    out = tmp_path / "task-level.md"
    assert main(["task-report", "--batches", "suite", "--out", str(out)]) == 0
    assert "| `buy-one` | keyboard-only | gate | 1 | 100% [" in out.read_text(encoding="utf-8")
