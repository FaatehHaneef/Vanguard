"""Several actions per model call, call accounting, `usage` and batch --max-calls."""

import asyncio
from datetime import UTC, datetime

import pytest

from vanguard import batch, catalog, usage
from vanguard.agent import run_once
from vanguard.agent.prompts import system_prompt
from vanguard.checker import check_run
from vanguard.contracts import (
    Action,
    BatchRequest,
    EnforcementOption,
    GateDecision,
    Observation,
    PerceptionMode,
    RunConfig,
    RunOutcome,
    StepRecord,
)
from vanguard.executor import FakeExecutor
from vanguard.providers import ScriptedProvider
from vanguard.providers.base import parse_calls
from vanguard.settings import Settings
from vanguard.store import RunStore

SITE = catalog.site("tallowmere")
TASK = catalog.task("buy-one")
TAB = Action(tool="press", key="Tab")
ENTER = Action(tool="press", key="Enter")


@pytest.fixture
def store():
    store = RunStore("sqlite:///:memory:")
    store.create_schema()
    return store


def run(store, script, per_call, persona_id="keyboard-only", max_steps=20):
    config = RunConfig(
        site_id=SITE.id,
        task_id=TASK.id,
        persona_id=persona_id,
        enforcement=[EnforcementOption.GATE],
        provider="fake",
        actions_per_call=per_call,
    )
    summary = store.create_run(config)
    provider = ScriptedProvider(script)
    result = asyncio.run(
        run_once(
            summary.id,
            config,
            catalog.persona(persona_id),
            SITE,
            TASK,
            provider,
            FakeExecutor(),
            store,
            allowed_origins=[SITE.origin],
            max_steps=max_steps,
            stuck_after=5,
        )
    )
    return result, store.steps(summary.id), provider


def test_one_call_runs_several_actions_until_the_page_changes(store):
    # Tab keeps the page; Enter follows the link, so the call's last two actions are dropped.
    script = [[TAB, ENTER, TAB, ENTER]] * 4
    summary, steps, provider = run(store, script, per_call=4)
    assert summary.outcome is RunOutcome.SUCCESS
    assert [(s.call, s.in_call) for s in steps[:3]] == [(0, 0), (0, 1), (1, 0)]
    assert provider.calls < len(steps)
    assert usage.calls_in(steps) == provider.calls


def test_a_refused_action_ends_the_call(store):
    click = Action(tool="click", ref="e0", rationale="shortcut")
    script = [[TAB, click, ENTER], *[[TAB, ENTER]] * 4]
    summary, steps, _ = run(store, script, per_call=3)
    assert steps[1].gate.rule == "H1" and not steps[1].executed
    assert (steps[2].call, steps[2].in_call) == (1, 0)  # the Enter after it never ran
    assert summary.outcome is RunOutcome.SUCCESS


def test_one_action_per_call_ignores_the_rest(store):
    summary, steps, provider = run(store, [[TAB, ENTER]] * 8, per_call=1)
    assert all(step.in_call == 0 for step in steps)
    assert provider.calls == len(steps)


def test_tokens_are_counted_once_per_call(store):
    _, steps, _ = run(store, [[TAB, ENTER]] * 4, per_call=4)
    assert all(s.input_tokens == 0 and s.output_tokens == 0 for s in steps if s.in_call)


def test_parse_calls_stops_at_the_first_unusable_call():
    good = ("press", {"key": "Tab"})
    bad = ("press", {})
    actions, error = parse_calls([good, bad, good], max_actions=4)
    assert [a.key for a in actions] == ["Tab"] and error is None
    actions, error = parse_calls([bad, good], max_actions=4)
    assert actions == [] and error
    assert len(parse_calls([good] * 5, max_actions=2)[0]) == 2


def test_the_prompt_mentions_several_actions_only_when_allowed():
    persona = catalog.persona("keyboard-only")
    assert "up to 4 tools" in system_prompt(persona, 4)
    assert "exactly one" in system_prompt(persona, 1)


def _step(index, in_call, observation, action):
    return StepRecord(
        run_id="r",
        index=index,
        started_at=datetime.now(UTC),
        observation=observation,
        proposed=action,
        gate=GateDecision(allowed=True),
        executed=True,
        call=0,
        in_call=in_call,
    )


def test_chained_observations_do_not_count_as_seen():
    """A later action of a call was planned on the call's first observation, so a link
    that only appeared after the first action was never seen by the model."""
    persona = catalog.persona("first-time")
    first = Observation(mode=PerceptionMode.FULL, url=SITE.origin + "/", content="home")
    later = Observation(
        mode=PerceptionMode.FULL,
        url=SITE.origin + "/",
        content="[e1] link",
        links=[SITE.origin + "/staff"],
    )
    goto = Action(tool="goto", url=SITE.origin + "/staff")
    chained = check_run([_step(0, 0, first, TAB), _step(1, 1, later, goto)], persona, first.url)
    shown = check_run([_step(0, 0, first, TAB), _step(1, 0, later, goto)], persona, first.url)
    assert any(v.rule == "H4a" for v in chained.steps[1].attempted)
    assert not any(v.rule == "H4a" for v in shown.steps[1].attempted)


# ---------------------------------------------------------------- usage and --max-calls


def test_quota_day_starts_at_midnight_pacific():
    start = usage.quota_day_start(datetime(2026, 11, 24, 20, 0, tzinfo=UTC))
    assert start == datetime(2026, 11, 24, 8, 0, tzinfo=UTC)  # PST is UTC-8


def test_usage_counts_agent_and_verifier_calls(store):
    run(store, [[TAB, ENTER]] * 4, per_call=4)
    found = usage.usage_since(store, usage.quota_day_start())
    assert found.runs == 1 and found.agent_calls > 0 and found.verifier_calls == 0
    settings = Settings(gemini_api_keys=["a", "b"], calls_per_key_per_day=20)
    assert "left today: " + str(40 - found.calls) in usage.report(found, settings)


def test_batch_stops_before_going_past_max_calls(store, monkeypatch):
    monkeypatch.setenv("VANGUARD_EXECUTOR", "fake")
    settings = Settings(executor="fake", enabled_providers=["fake"], max_steps_per_run=3)
    request = BatchRequest(
        site_id=SITE.id,
        task_ids=[TASK.id],
        persona_ids=["keyboard-only"],
        enforcements=[[EnforcementOption.GATE]],
        provider="fake",
        repeats=10,
        max_calls=4,
    )
    request = batch.prepare(request, settings)
    final = asyncio.run(batch.run_batch(request, settings, store))
    assert final.stopped and final.stopped.startswith("call budget reached")
    runs = store.list_runs(request.batch_id, limit=100)
    used = sum(usage.calls_in(store.steps(r.id)) for r in runs)
    assert used == 4 and final.remaining == 6  # 3 calls allowed for the first run, then 1 each


def test_the_cli_opens_the_shared_store(monkeypatch, tmp_path):
    """Studio items are read through vanguard.deps, so CLI batches see custom items."""
    from vanguard import cli, deps
    from vanguard.settings import get_settings

    monkeypatch.setenv("VANGUARD_DATABASE_URL", f"sqlite:///{tmp_path / 'cli.db'}")
    get_settings.cache_clear()
    monkeypatch.setattr(deps, "_store", None)
    try:
        assert cli.main(["usage"]) == 0
        assert deps.get_store() is not None
    finally:
        get_settings.cache_clear()
