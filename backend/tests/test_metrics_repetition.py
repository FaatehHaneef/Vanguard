"""Repeated attempts (metrics/repetition.py), on hand-made step records."""

from datetime import UTC, datetime

from test_agent_loop import KEYS, run, store  # noqa: F401  (fixture)

from vanguard import catalog
from vanguard.checker import check_run
from vanguard.contracts import Action, EnforcementOption, GateDecision, Observation, StepRecord
from vanguard.metrics import group_metrics, repeated_attempts, run_metrics

PAGE = "http://localhost:3100/"
CART = "http://localhost:3100/cart"
ALLOWED = GateDecision(allowed=True)
REFUSED = GateDecision(allowed=False, rule="H1", message="not available")


def step(
    index: int,
    action: Action | None,
    *,
    url: str = PAGE,
    url_after: str | None = PAGE,
    focus_after: str | None = None,
    gate: GateDecision = ALLOWED,
) -> StepRecord:
    return StepRecord(
        run_id="r1",
        index=index,
        started_at=datetime(2026, 11, 24, tzinfo=UTC),
        observation=Observation(mode="full", url=url, content="page"),
        proposed=action,
        gate=gate,
        executed=gate.allowed,
        url_after=url_after if gate.allowed else None,
        focus_after=focus_after,
    )


tab = Action(tool="press", key="Tab")
enter = Action(tool="press", key="Enter")
escape = Action(tool="press", key="Escape")
click = Action(tool="click", ref="e3")


def test_no_steps_and_single_step():
    assert repeated_attempts([]) == 0
    assert repeated_attempts([step(0, enter)]) == 0


def test_tab_that_moves_focus_is_not_a_repeat():
    steps = [
        step(0, tab, focus_after="e1"),
        step(1, tab, focus_after="e2"),
        step(2, tab, focus_after="e3"),
    ]
    assert repeated_attempts(steps) == 0


def test_same_action_without_effect_counts_each_retry():
    # Escape three times, nothing changes: the second and third are repeats.
    steps = [step(0, escape), step(1, escape), step(2, escape)]
    assert repeated_attempts(steps) == 2


def test_focus_unchanged_after_the_previous_step_counts():
    # Focus is e5 after step 0, and Enter on step 1 leaves it at e5.
    steps = [
        step(0, tab, focus_after="e5"),
        step(1, enter, focus_after="e5"),
        step(2, enter, focus_after="e5"),
    ]
    assert repeated_attempts(steps) == 1


def test_a_change_of_url_or_focus_makes_the_retry_legitimate():
    to_cart = [step(0, enter, url_after=CART), step(1, enter, url=CART, url_after=CART)]
    assert repeated_attempts(to_cart) == 0
    moved = [step(0, enter, focus_after="e2"), step(1, enter, focus_after="e2")]
    assert repeated_attempts(moved) == 0


def test_retrying_a_refused_action_counts():
    steps = [step(0, click, gate=REFUSED), step(1, click, gate=REFUSED), step(2, tab)]
    assert repeated_attempts(steps) == 1


def test_different_targets_or_inputs_are_not_repeats():
    other_ref = Action(tool="click", ref="e4")
    typed_a = Action(tool="type", text="Sara Khan")
    typed_b = Action(tool="type", text="sara@example.com")
    assert repeated_attempts([step(0, click, gate=REFUSED), step(1, other_ref)]) == 0
    assert repeated_attempts([step(0, typed_a), step(1, typed_b)]) == 0
    assert repeated_attempts([step(0, tab), step(1, enter)]) == 0


def test_invalid_output_breaks_a_run_of_repeats():
    steps = [step(0, escape), step(1, None), step(2, escape)]
    assert repeated_attempts(steps) == 0


def test_steps_are_taken_in_index_order():
    steps = [step(2, escape), step(0, escape), step(1, escape)]
    assert repeated_attempts(steps) == 2


def test_run_and_group_metrics_report_repeated_attempts(store):  # noqa: F811
    keyboard = catalog.persona("keyboard-only")
    blocked_click = Action(tool="click", ref="e0", rationale="shortcut")
    script = [blocked_click, blocked_click, blocked_click, *KEYS]
    runs = []
    for _ in range(2):
        summary = run(store, "keyboard-only", [EnforcementOption.GATE], script)
        summary = store.get_run(summary.id)
        steps = store.steps(summary.id)
        metrics = run_metrics(summary, steps, check_run(steps, keyboard, PAGE))
        assert metrics.repeated_attempts == 2
        runs.append((summary, metrics, steps))
    (group,) = group_metrics(runs)
    assert group.mean_repeated_attempts == 2.0
