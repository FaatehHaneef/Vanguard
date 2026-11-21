import asyncio

from test_agent_loop import SITE, TASK, store  # noqa: F401  (fixture)

from vanguard import catalog, verifier
from vanguard.agent import run_once
from vanguard.checker import check_run
from vanguard.contracts import (
    Action,
    EnforcementOption,
    Observation,
    PerceptionMode,
    RunConfig,
)
from vanguard.executor import FakeExecutor
from vanguard.metrics import run_metrics
from vanguard.providers import ScriptedProvider

keyboard = catalog.persona("keyboard-only")
click = Action(tool="click", ref="e0", rationale="shortcut")
tab = Action(tool="press", key="Tab")
obs = Observation(mode=PerceptionMode.FULL, url="http://localhost:3100/", content="[e0] link")


def test_verify_decisions():
    refuse = ScriptedProvider(json_replies=[{"allowed": False, "reason": "No mouse."}])
    decision = asyncio.run(verifier.verify(refuse, click, keyboard, obs))
    assert not decision.allowed and decision.rule == "V" and decision.message == "No mouse."
    allow = ScriptedProvider(json_replies=[{"allowed": True, "reason": ""}])
    assert asyncio.run(verifier.verify(allow, tab, keyboard, obs)).allowed
    # No usable answer: allowed, with the failure recorded.
    silent = asyncio.run(verifier.verify(ScriptedProvider(), tab, keyboard, obs))
    assert silent.allowed and "no decision" in silent.message


def test_verifier_in_the_loop_and_its_scores(store):  # noqa: F811
    config = RunConfig(
        site_id=SITE.id,
        task_id=TASK.id,
        persona_id="keyboard-only",
        enforcement=[EnforcementOption.VERIFIER],
        provider="fake",
    )
    summary = store.create_run(config)
    # The verifier lets the click through (a miss) and refuses a Tab (a false alarm),
    # then allows everything.
    provider = ScriptedProvider(
        [click, tab, tab],
        json_replies=[
            {"allowed": True, "reason": ""},
            {"allowed": False, "reason": "looks risky"},
            {"allowed": True, "reason": ""},
        ],
    )
    asyncio.run(
        run_once(
            summary.id,
            config,
            keyboard,
            SITE,
            TASK,
            provider,
            FakeExecutor(),
            store,
            allowed_origins=[SITE.origin],
            max_steps=4,
            stuck_after=10,
        )
    )
    steps = store.steps(summary.id)
    assert steps[0].executed and steps[0].verifier.allowed
    assert not steps[1].executed and steps[1].gate.rule == "V"
    leakage = check_run(steps, keyboard, SITE.origin + TASK.start_path)
    metrics = run_metrics(store.get_run(summary.id), steps, leakage)
    assert metrics.verifier_steps == 3
    assert metrics.verifier_precision == 0.0 and metrics.verifier_recall == 0.0
