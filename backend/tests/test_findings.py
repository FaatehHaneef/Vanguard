"""Findings and failure attribution (vanguard.findings), from hand-made records."""

from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient

from vanguard import findings
from vanguard.checker import RunLeakage
from vanguard.contracts import (
    Action,
    GateDecision,
    Observation,
    PerceptionMode,
    RunConfig,
    RunOutcome,
    RunStatus,
    RunSummary,
    StepRecord,
)
from vanguard.contracts.findings import Attribution, FindingKind
from vanguard.failures import RunFailure
from vanguard.settings import get_settings

HOME = "http://localhost:3101/"
PAGE = '[e4] link "Request a callback" -> /callback.html\n[e9] generic "10:00"'


def step(index, action, allowed=True, focus=None, url=HOME, error=None, content=PAGE):
    return StepRecord(
        run_id="r1",
        index=index,
        started_at=datetime.now(UTC),
        observation=Observation(mode=PerceptionMode.FULL, url=url, content=content),
        proposed=action,
        gate=GateDecision(allowed=allowed, rule=None if allowed else "H1", message="no pointer"),
        executed=allowed,
        execution_error=error,
        url_after=url,
        focus_after=focus,
    )


def click(ref):
    return Action(tool="click", ref=ref, rationale="pick it")


TAB = Action(tool="press", key="Tab")
NO_LEAKS = RunLeakage(run_id="r1", steps=[])


def test_a_control_never_reached_within_the_limits_is_inaccessible():
    steps = [step(0, click("e9"), allowed=False), step(1, TAB, focus="e4")]
    [found] = findings.inaccessible_controls(steps, NO_LEAKS)
    assert found.kind is FindingKind.INACCESSIBLE_CONTROL
    assert found.element == 'generic "10:00"' and found.steps == [0]


def test_a_refused_click_on_a_control_reached_by_keyboard_is_not_a_finding():
    steps = [step(0, click("e4"), allowed=False), step(1, TAB, focus="e4")]
    assert findings.inaccessible_controls(steps, NO_LEAKS) == []


def test_repeating_an_action_without_effect():
    escape = Action(tool="press", key="Escape")
    steps = [step(0, escape), step(1, escape), step(2, escape), step(3, TAB, focus="e4")]
    assert findings.repeated_steps(steps) == [1, 2]
    refused = [step(0, click("e9"), allowed=False), step(1, click("e9"), allowed=False)]
    assert findings.repeated_steps(refused) == [1]


def test_going_round_the_same_pages_is_a_confusing_workflow():
    other = "http://localhost:3101/book.html"
    urls = [HOME, other, HOME, other, HOME, other]
    steps = [step(i, TAB, url=url) for i, url in enumerate(urls)]
    summary = run("wb-callback", "keyboard-only", RunOutcome.SUCCESS)
    kinds = findings.confusing_workflow(summary, steps, control_steps=[2, 3, 2])
    summaries = [item.summary for item in kinds]
    assert any("6 steps where the control needed about 2" in s for s in summaries)
    assert any("Came back to / 3 times" in s for s in summaries)


# ---------------------------------------------------------------- attribution


def run(task, persona, outcome, run_id="r1", batch="b"):
    config = RunConfig(
        site_id="willowbrook", task_id=task, persona_id=persona, provider="fake", batch_id=batch
    )
    return RunSummary(
        id=run_id,
        config=config,
        status=RunStatus.FINISHED,
        outcome=outcome,
        created_at=datetime.now(UTC),
    )


def failure(primary):
    return RunFailure(run_id="r1", label="x", outcome="gave_up", primary=primary)


def controls(task, wins, losses):
    return [run(task, "unrestricted", RunOutcome.SUCCESS, f"c{i}") for i in range(wins)] + [
        run(task, "unrestricted", RunOutcome.GAVE_UP, f"d{i}") for i in range(losses)
    ]


def attribute(task, persona, steps, primary, control_runs):
    summary = run(task, persona, RunOutcome.GAVE_UP)
    return findings.attribute(summary, steps, NO_LEAKS, failure(primary), control_runs)


def test_the_site_when_the_control_fails_too():
    result = attribute("wb-callback", "keyboard-only", [step(0, TAB)], "gave_up",
                       controls("wb-callback", 1, 3))  # fmt: skip
    assert result.attribution is Attribution.SITE and result.control_success_rate == 0.25


def test_the_restriction_when_the_site_plants_a_barrier_for_the_persona():
    result = attribute("wb-book-tuesday", "keyboard-only", [step(0, TAB)], "gave_up",
                       controls("wb-book-tuesday", 3, 0))  # fmt: skip
    assert result.attribution is Attribution.RESTRICTION
    assert result.expected.startswith("blocked")


def test_the_restriction_when_a_control_stays_out_of_reach():
    steps = [step(0, click("e9"), allowed=False), step(1, TAB, focus="e4")]
    result = attribute("wb-callback", "keyboard-only", steps, "gave_up",
                       controls("wb-callback", 3, 0))  # fmt: skip
    assert result.attribution is Attribution.RESTRICTION
    assert "10:00" in result.reason


def test_the_agent_when_the_control_succeeds_and_no_limit_explains_it():
    steps = [step(0, click("e4"), allowed=False), *[step(i, TAB, focus="e4") for i in range(1, 8)]]
    result = attribute("wb-callback", "keyboard-only", steps, "step_limit",
                       controls("wb-callback", 3, 0))  # fmt: skip
    assert result.attribution is Attribution.AGENT


def test_infrastructure_and_unknown():
    infra = attribute("wb-callback", "keyboard-only", [], "model_unavailable", [])
    assert infra.attribution is Attribution.INFRASTRUCTURE
    unknown = attribute("wb-callback", "keyboard-only", [step(0, TAB)], "gave_up", [])
    assert unknown.attribution is Attribution.UNKNOWN


# ---------------------------------------------------------------- API


@pytest.fixture
def client(monkeypatch, tmp_path):
    monkeypatch.setenv("VANGUARD_DATABASE_URL", f"sqlite:///{tmp_path / 'test.db'}")
    monkeypatch.setenv("VANGUARD_EXECUTOR", "fake")
    monkeypatch.setenv("VANGUARD_ENABLED_PROVIDERS", '["fake"]')
    get_settings.cache_clear()
    from vanguard.api import app

    with TestClient(app) as client:
        yield client
    get_settings.cache_clear()


def test_findings_endpoints(client):
    body = {"site_id": "tallowmere", "task_id": "buy-one", "persona_id": "keyboard-only",
            "provider": "fake", "batch_id": "f1"}  # fmt: skip
    run_id = client.post("/runs", json=body).json()["id"]
    report = client.get(f"/runs/{run_id}/findings").json()
    assert report["limits_statement"].startswith("Simulated users cannot establish")
    assert report["runs"] == 1 and report["attributions"][0]["attribution"] == "unknown"
    assert client.get("/findings", params={"batches": ["f1"]}).json()["runs"] == 1
    assert client.get("/findings", params={"batches": ["nope"]}).status_code == 404
    assert client.get("/runs/nope/findings").status_code == 404
