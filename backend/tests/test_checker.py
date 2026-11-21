"""The checker re-scores recorded runs with the same rules the gate uses."""

from datetime import UTC, datetime

from test_agent_loop import KEYS, run, store  # noqa: F401  (fixture)

from vanguard import catalog
from vanguard.checker import check_run, check_step
from vanguard.contracts import (
    Action,
    BrowserEvent,
    EnforcementOption,
    GateDecision,
    LimitId,
    Observation,
    PerceptionMode,
    StepRecord,
)
from vanguard.gate import ActionGate
from vanguard.rules import RuleContext

ORIGIN = "http://localhost:3100"
START = f"{ORIGIN}/"
keyboard = catalog.persona("keyboard-only")
control = catalog.persona("unrestricted")
first_time = catalog.persona("first-time")


def step(index, action, *, executed=True, events=(), links=(), allowed=True, url=START):
    return StepRecord(
        run_id="r",
        index=index,
        started_at=datetime.now(UTC),
        observation=Observation(mode=PerceptionMode.FULL, url=url, content="", links=list(links)),
        proposed=action,
        gate=GateDecision(allowed=allowed, rule=None if allowed else "H1"),
        executed=executed,
        events=list(events),
    )


click = Action(tool="click", ref="e3")
tab = Action(tool="press", key="Tab")
pointer = BrowserEvent(type="pointerdown", trusted=True, target="e3")


def test_blocked_click_is_attempted_not_executed():
    verdict = check_step(step(0, click, executed=False, allowed=False), keyboard, START)
    assert [v.rule for v in verdict.attempted] == ["H1"]
    assert verdict.executed == []


def test_executed_click_is_executed_leakage():
    verdict = check_step(step(0, click, events=[pointer]), keyboard, START)
    assert [v.rule for v in verdict.executed] == ["H1"]  # not doubled by the browser check


def test_browser_evidence_catches_pointer_input_behind_a_keyboard_tool():
    verdict = check_step(step(0, tab, events=[pointer]), keyboard, START)
    assert [v.rule for v in verdict.executed] == ["H1"]
    untrusted = BrowserEvent(type="pointerdown", trusted=False)
    assert check_step(step(0, tab, events=[untrusted]), keyboard, START).executed == []


def test_keyboard_steps_are_clean():
    keydown = BrowserEvent(type="keydown", trusted=True, target="Tab")
    verdict = check_step(step(0, tab, events=[keydown]), keyboard, START)
    assert verdict.attempted == [] and verdict.executed == []


def test_h4a_uses_links_seen_in_earlier_steps():
    steps = [
        step(0, tab, links=[f"{ORIGIN}/cart"]),
        step(1, Action(tool="goto", url="/cart")),
        step(2, Action(tool="goto", url="/checkout")),
    ]
    leakage = check_run(steps, first_time, START)
    assert [bool(v.executed) for v in leakage.steps] == [False, False, True]
    assert leakage.by_limit() == {LimitId.FIRST_TIME_KNOWLEDGE: 1}


def test_control_is_scored_against_every_limit():
    steps = [step(0, click, events=[pointer]), step(1, Action(tool="goto", url="/checkout"))]
    leakage = check_run(steps, control, START)
    assert leakage.executed_steps == 2
    assert set(leakage.by_limit()) == {LimitId.NO_POINTER, LimitId.FIRST_TIME_KNOWLEDGE}


def test_checker_agrees_with_gate_on_every_proposal():
    gate = ActionGate(keyboard, [EnforcementOption.GATE])
    ctx = RuleContext(current_url=START, start_url=START, allowed_origins=[ORIGIN])
    for action in [click, tab, Action(tool="wheel", dx=0, dy=100), Action(tool="goto", url="/")]:
        blocked = not gate.decide(action, ctx).allowed
        flagged = bool(check_step(step(0, action, executed=False), keyboard, START).attempted)
        assert blocked == flagged, action.tool


def test_checker_on_recorded_runs(store):  # noqa: F811
    prompt_only = run(store, "keyboard-only", [EnforcementOption.PROMPT_ONLY], [click, *KEYS])
    gated = run(store, "keyboard-only", [EnforcementOption.GATE], [click, *KEYS])
    loose = check_run(store.steps(prompt_only.id), keyboard, START)
    strict = check_run(store.steps(gated.id), keyboard, START)
    assert (loose.attempted_steps, loose.executed_steps) == (1, 1)
    assert (strict.attempted_steps, strict.executed_steps) == (1, 0)


def test_h3a_outside_the_magnified_window():
    from vanguard.contracts import Rect

    iris = catalog.persona("magnifier")
    window = Rect(x=0, y=0, width=320, height=180)

    def magnified(action, box=None, content='[e1] button "Add"', executed=True):
        record = step(0, action, executed=executed)
        record.observation = Observation(
            mode=PerceptionMode.MAGNIFIED, url=START, content=content, window=window
        )
        record.target_box = box
        return record

    inside = magnified(Action(tool="click", ref="e1"), Rect(x=10, y=10, width=50, height=20))
    assert check_step(inside, iris, START).executed == []
    unseen = magnified(Action(tool="click", ref="e9"), executed=False)
    verdict = check_step(unseen, iris, START)
    assert [v.rule for v in verdict.attempted] == ["H3a"] and verdict.executed == []
    moved = magnified(Action(tool="click", ref="e1"), Rect(x=900, y=600, width=50, height=20))
    assert [v.rule for v in check_step(moved, iris, START).executed] == ["H3a"]
    # Full-view steps never trigger H3a, even for the control persona.
    assert check_step(step(0, Action(tool="click", ref="e9")), iris, START).attempted == []
