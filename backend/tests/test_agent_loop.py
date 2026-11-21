import asyncio

import pytest

from vanguard import catalog
from vanguard.agent import run_once
from vanguard.contracts import Action, EnforcementOption, RunConfig, RunOutcome
from vanguard.executor import FakeExecutor
from vanguard.providers import ScriptedProvider
from vanguard.store import RunStore

SITE = catalog.site("tallowmere")
TASK = catalog.task("buy-one")
KEYS = [Action(tool="press", key=key) for key in ["Tab", "Enter"] * 4]


@pytest.fixture
def store():
    store = RunStore("sqlite:///:memory:")
    store.create_schema()
    return store


def run(store, persona_id, enforcement, script, stuck_after=5, max_steps=20):
    config = RunConfig(
        site_id=SITE.id,
        task_id=TASK.id,
        persona_id=persona_id,
        enforcement=enforcement,
        provider="fake",
    )
    summary = store.create_run(config)
    return asyncio.run(
        run_once(
            summary.id,
            config,
            catalog.persona(persona_id),
            SITE,
            TASK,
            ScriptedProvider(script),
            FakeExecutor(),
            store,
            allowed_origins=[SITE.origin],
            max_steps=max_steps,
            stuck_after=stuck_after,
        )
    )


def test_keyboard_route_succeeds(store):
    summary = run(store, "keyboard-only", [EnforcementOption.GATE], KEYS)
    assert summary.outcome is RunOutcome.SUCCESS
    assert summary.blocked == 0
    events = [event.type for step in store.steps(summary.id) for event in step.events]
    assert set(events) == {"keydown"}


def test_gate_blocks_click_and_run_continues(store):
    script = [Action(tool="click", ref="e0", rationale="shortcut"), *KEYS]
    summary = run(store, "keyboard-only", [EnforcementOption.GATE], script)
    steps = store.steps(summary.id)
    assert summary.outcome is RunOutcome.SUCCESS and summary.blocked == 1
    assert steps[0].gate.rule == "H1" and not steps[0].executed


def test_prompt_only_lets_click_through_and_records_pointer_event(store):
    script = [Action(tool="click", ref="e0", rationale="shortcut")]
    summary = run(store, "keyboard-only", [EnforcementOption.PROMPT_ONLY], script)
    first = store.steps(summary.id)[0]
    assert first.executed and [event.type for event in first.events] == ["pointerdown"]


def test_stuck_is_detected(store):
    script = [Action(tool="press", key="Escape")] * 10
    summary = run(store, "keyboard-only", [EnforcementOption.GATE], script, stuck_after=3)
    assert summary.outcome is RunOutcome.STUCK and summary.steps == 3


def test_unsafe_navigation_is_blocked_for_control(store):
    script = [Action(tool="goto", url="https://www.paypal.com/")]
    summary = run(store, "unrestricted", [EnforcementOption.PROMPT_ONLY], script)
    assert store.steps(summary.id)[0].gate.rule == "S0"
