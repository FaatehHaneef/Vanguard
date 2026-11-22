from test_agent_loop import KEYS, run, store  # noqa: F401  (fixture)

from vanguard import catalog, failures
from vanguard.checker import check_run
from vanguard.contracts import Action, EnforcementOption

START = "http://localhost:3100/"
keyboard = catalog.persona("keyboard-only")
click = Action(tool="click", ref="e0", rationale="shortcut")


def classify(store, enforcement, script, **kwargs):  # noqa: F811
    summary = run(store, "keyboard-only", enforcement, script, **kwargs)
    summary = store.get_run(summary.id)
    steps = store.steps(summary.id)
    return failures.classify(summary, steps, check_run(steps, keyboard, START))


def test_success_without_leak_is_not_a_failure(store):  # noqa: F811
    item = classify(store, [EnforcementOption.GATE], KEYS)
    assert item.outcome == "success" and not failures.is_failure(item)


def test_success_with_executed_leak_is_a_failure(store):  # noqa: F811
    item = classify(store, [EnforcementOption.PROMPT_ONLY], [click])
    assert "persona_leak" in item.tags and failures.is_failure(item)
    assert item.primary == "persona_leak"


def test_refusal_loop_and_gave_up(store):  # noqa: F811
    item = classify(store, [EnforcementOption.GATE], [click] * 4)
    assert item.tags == ["refusal_loop", "gave_up"]
    assert item.primary == "refusal_loop"


def test_stuck_and_grouping(store):  # noqa: F811
    stuck = classify(
        store, [EnforcementOption.GATE], [Action(tool="press", key="Escape")] * 9, stuck_after=3
    )
    quitter = classify(store, [EnforcementOption.GATE], [])
    assert stuck.primary == "stuck" and quitter.primary == "gave_up"
    groups = failures.group([stuck, quitter, stuck])
    assert [(cause, count) for cause, _, count, _ in groups] == [("stuck", 2), ("gave_up", 1)]
    table = failures.markdown([stuck, quitter])
    assert "| stuck | 1 |" in table and "2 failing runs" in table


def test_wrong_answer(store):  # noqa: F811
    item = classify(store, [EnforcementOption.GATE], [Action(tool="done", answer="all bought")])
    assert item.primary == "wrong_answer" and "all bought" in item.detail


def test_control_leaks_are_a_reference_not_a_failure(store):  # noqa: F811
    from vanguard.contracts import EnforcementOption as E

    summary = run(store, "unrestricted", [E.PROMPT_ONLY], [click, *KEYS])
    summary = store.get_run(summary.id)
    steps = store.steps(summary.id)
    control = catalog.persona("unrestricted")
    item = failures.classify(summary, steps, check_run(steps, control, START))
    assert "persona_leak" not in item.tags and not failures.is_failure(item)
