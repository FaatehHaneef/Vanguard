"""Model calls vs actions in the run and group metrics (several actions per call)."""

import asyncio

from test_agent_loop import SITE, TASK, store  # noqa: F401  (fixture)

from vanguard import catalog
from vanguard.agent import run_once
from vanguard.checker import check_run
from vanguard.contracts import Action, EnforcementOption, RunConfig
from vanguard.executor import FakeExecutor
from vanguard.metrics import group_metrics, run_metrics
from vanguard.providers import ScriptedProvider

START = "http://localhost:3100/"
keyboard = catalog.persona("keyboard-only")
tab = Action(tool="press", key="Tab")
enter = Action(tool="press", key="Enter")
# The fake shop's keyboard route: Tab, Enter on each of its four pages.
ROUTE = [tab, enter] * 4


def run_with(store, script, actions_per_call):  # noqa: F811
    config = RunConfig(
        site_id=SITE.id,
        task_id=TASK.id,
        persona_id="keyboard-only",
        enforcement=[EnforcementOption.GATE],
        provider="fake",
        actions_per_call=actions_per_call,
    )
    summary = store.create_run(config)
    asyncio.run(
        run_once(
            summary.id,
            config,
            keyboard,
            SITE,
            TASK,
            ScriptedProvider(script),
            FakeExecutor(),
            store,
            allowed_origins=[SITE.origin],
            max_steps=20,
            stuck_after=5,
        )
    )
    summary = store.get_run(summary.id)
    steps = store.steps(summary.id)
    return summary, run_metrics(summary, steps, check_run(steps, keyboard, START)), steps


def test_one_action_per_call_makes_one_call_per_action(store):  # noqa: F811
    _, metrics, steps = run_with(store, ROUTE, actions_per_call=1)
    assert metrics.success
    assert metrics.actions == metrics.steps == len(steps) == 8
    assert metrics.model_calls == 8


def test_several_actions_per_call_count_once(store):  # noqa: F811
    # Four calls of Tab then Enter (Enter changes the page, which ends a call):
    # the same eight actions, half the calls.
    script = [[tab, enter]] * 4
    _, metrics, steps = run_with(store, script, actions_per_call=4)
    assert metrics.success
    assert metrics.actions == 8
    assert metrics.model_calls == 4
    assert [step.in_call for step in steps] == [0, 1] * 4


def test_group_means_for_calls_and_actions(store):  # noqa: F811
    runs = [
        run_with(store, ROUTE, actions_per_call=1),
        run_with(store, [[tab, enter]] * 4, actions_per_call=4),
    ]
    (group,) = group_metrics(runs)
    assert group.mean_actions == 8.0
    assert group.mean_model_calls == 6.0  # (8 + 4) / 2
