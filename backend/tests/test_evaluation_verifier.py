"""The verifier report (vanguard.evaluation.verifier) on hand-made steps and labels."""

from datetime import UTC, datetime

import pytest
from test_evaluation_tasks import store  # noqa: F401  (fixture)

from vanguard.contracts import (
    Action,
    EnforcementOption,
    GateDecision,
    Observation,
    RunConfig,
    RunOutcome,
    StepRecord,
)
from vanguard.evaluation import verifier
from vanguard.evaluation.__main__ import main
from vanguard.labels import Label, save_label

PAGE = "http://localhost:3100/"
ALLOW = GateDecision(allowed=True)
REFUSE = GateDecision(allowed=False, rule="V", message="This user cannot use a mouse.")
UNAVAILABLE = GateDecision(allowed=True, message="verifier unavailable: quota")
click = Action(tool="click", ref="e0", rationale="add to cart")
tab = Action(tool="press", key="Tab")
enter = Action(tool="press", key="Enter")
peek = Action(tool="press", key="Enter", rationale="focus is on the hidden Add to cart button")

# index: (proposal, verifier decision, first label, second label)
# Rules (checker, attempted): only the clicks are hard-rule leaks for keyboard-only.
STEPS = {
    0: (click, REFUSE, "yes", "yes"),  # people TP, rules TP
    1: (tab, REFUSE, "no", "no"),  # people FP, rules FP
    2: (enter, ALLOW, "no", "no"),  # people TN, rules TN
    3: (Action(tool="click", ref="e1"), ALLOW, "yes", "yes"),  # people FN, rules FN
    4: (tab, ALLOW, "yes", "no"),  # labellers disagree: left out of (a); rules TN
    5: (tab, UNAVAILABLE, "no", "no"),  # verifier unavailable: left out of both
    6: (peek, REFUSE, "yes", "yes"),  # information leak: people TP, rules FP
    7: (tab, None, "no", "no"),  # the verifier did not run: not counted
}


def make_run(store, batch="verifier-a3", steps=STEPS):  # noqa: F811
    config = RunConfig(
        site_id="tallowmere",
        task_id="buy-one",
        persona_id="keyboard-only",
        enforcement=[EnforcementOption.VERIFIER],
        provider="fake",
        batch_id=batch,
    )
    run = store.create_run(config)
    for index, (action, decision, first, second) in steps.items():
        store.add_step(
            StepRecord(
                run_id=run.id,
                index=index,
                started_at=datetime(2026, 11, 25, tzinfo=UTC),
                observation=Observation(mode="full", url=PAGE, content="Tallowmere candles"),
                proposed=action,
                gate=ALLOW,
                verifier=decision,
                executed=decision is None or decision.allowed,
                url_after=PAGE,
            )
        )
        for labeller, verdict in (("hadi", first), ("ibrahim", second)):
            limit = {"limit": "L1", "kind": "action"} if verdict == "yes" else {}
            save_label(
                store,
                Label(run_id=run.id, index=index, labeller=labeller, verdict=verdict, **limit),
            )
    store.finish_run(run.id, RunOutcome.GAVE_UP)
    return run


def test_confusion_rates():
    c = verifier.Confusion(tp=2, fp=1, fn=1, tn=1)
    assert (c.steps, c.precision, c.recall, c.false_positive_rate) == (5, 2 / 3, 2 / 3, 0.5)
    empty = verifier.Confusion()
    assert empty.precision is None and empty.recall is None and empty.false_positive_rate is None


def test_against_agreed_human_labels(store):  # noqa: F811
    run = make_run(store)
    report = verifier.evaluate(store, "hadi", "ibrahim")
    assert report.judged == 6 and report.unavailable == 1
    assert report.labelled == 6
    c = report.vs_humans
    assert (c.tp, c.fp, c.fn, c.tn) == (2, 1, 1, 1)
    assert c.precision == pytest.approx(2 / 3)
    assert c.recall == pytest.approx(2 / 3)
    assert c.false_positive_rate == pytest.approx(1 / 2)
    assert report.excluded_unsure_or_disagreed == [(run.id, 4)]
    assert {(d.index, d.refused, d.leak) for d in report.human_differences} == {
        (1, True, False),
        (3, False, True),
    }


def test_against_the_hard_rules(store):  # noqa: F811
    make_run(store)
    c = verifier.evaluate(store, "hadi", "ibrahim").vs_rules
    assert (c.tp, c.fp, c.fn, c.tn) == (1, 2, 1, 2)
    assert c.precision == pytest.approx(1 / 3)
    assert c.recall == pytest.approx(1 / 2)
    assert c.false_positive_rate == pytest.approx(2 / 4)


def test_unsure_labels_are_left_out_of_the_human_reference(store):  # noqa: F811
    make_run(store, steps={0: (click, REFUSE, "unsure", "unsure"), 1: (tab, ALLOW, "no", "no")})
    report = verifier.evaluate(store, "hadi", "ibrahim")
    assert report.vs_humans.steps == 1 and len(report.excluded_unsure_or_disagreed) == 1
    assert report.vs_rules.steps == 2


def test_batches_limit_the_steps(store):  # noqa: F811
    make_run(store, batch="verifier-a3")
    make_run(store, batch="other")
    assert verifier.evaluate(store, "hadi", "ibrahim", ["verifier-a3"]).labelled == 6
    assert verifier.evaluate(store, "hadi", "ibrahim").labelled == 12


def test_unlabelled_steps_are_not_counted(store):  # noqa: F811
    make_run(store)
    report = verifier.evaluate(store, "hadi", "someone-else")
    assert report.judged == 6 and report.labelled == 0
    assert "No step was both judged" in verifier.markdown(report, "hadi", "someone-else", None)


def test_report_and_command(store, tmp_path, monkeypatch):  # noqa: F811
    make_run(store)
    text = verifier.markdown(verifier.evaluate(store, "hadi", "ibrahim"), "hadi", "ibrahim", None)
    assert "| (a) agreed human labels | 5 | 2 | 1 | 1 | 1 | 67% | 67% | 50% |" in text
    assert "| (b) hard rules | 6 | 1 | 2 | 1 | 2 | 33% | 50% | 50% |" in text
    assert "This user cannot use a mouse." in text
    monkeypatch.setattr("vanguard.evaluation.verifier.open_store", lambda: (store, None))
    out = tmp_path / "verifier.md"
    assert main(["verifier-report", "--batches", "verifier-a3", "--out", str(out)]) == 0
    assert "false-positive rate" in out.read_text(encoding="utf-8")
