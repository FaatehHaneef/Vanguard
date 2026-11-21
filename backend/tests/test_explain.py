import asyncio

from test_agent_loop import KEYS, run, store  # noqa: F401  (fixture)
from test_api import client  # noqa: F401  (fixture)

from vanguard import catalog, explain
from vanguard.checker import check_run
from vanguard.contracts import Action, EnforcementOption
from vanguard.providers import ScriptedProvider

START = "http://localhost:3100/"
keyboard = catalog.persona("keyboard-only")
click = Action(tool="click", ref="e0", rationale="shortcut")


def facts_for(store, enforcement, script):  # noqa: F811
    summary = run(store, "keyboard-only", enforcement, script)
    summary = store.get_run(summary.id)
    steps = store.steps(summary.id)
    leakage = check_run(steps, keyboard, START)
    return explain.build_facts(summary, steps, leakage, keyboard, catalog.task("buy-one"))


def test_facts_and_template(store):  # noqa: F811
    facts = facts_for(store, [EnforcementOption.GATE], [click, *KEYS])
    assert facts["outcome"] == "completed the task" and facts["refusedSteps"] == 1
    assert [f["kind"] for f in facts["findings"]] == ["refused"]
    text = explain.builtin_explanation(facts)
    assert text.source == "builtin" and "Knock completed the task" in text.headline
    assert len(text.notes) == 1 and "click" in text.notes[0].why


def answer(story, notes=1):
    return {
        "headline": "Knock got there with the keyboard",
        "story": story,
        "notes": [
            {"index": i, "why": "A mouse is not an option for this person."} for i in range(notes)
        ],
    }


def test_checked_mode_rejects_invented_numbers(store):  # noqa: F811
    facts = facts_for(store, [EnforcementOption.GATE], [click, *KEYS])
    steps = facts["steps"]
    good = ScriptedProvider(json_replies=[answer(f"Knock finished in {steps} steps.")])
    result = asyncio.run(explain.explain_run(facts, good, "checked"))
    assert result.source == "ai" and result.rejected is None

    bad = ScriptedProvider(json_replies=[answer("Knock finished in 4321 steps.")])
    result = asyncio.run(explain.explain_run(facts, bad, "checked"))
    assert result.source == "builtin" and "4321" in result.rejected

    unchecked = ScriptedProvider(json_replies=[answer("Knock finished in 4321 steps.")])
    result = asyncio.run(explain.explain_run(facts, unchecked, "llm"))
    assert result.source == "ai"  # the unchecked alternative keeps it


def test_missing_notes_and_no_reply(store):  # noqa: F811
    facts = facts_for(store, [EnforcementOption.GATE], [click, *KEYS])
    skipped = ScriptedProvider(json_replies=[answer("Knock got there.", notes=0)])
    result = asyncio.run(explain.explain_run(facts, skipped, "checked"))
    assert result.source == "builtin" and "left out" in result.rejected
    result = asyncio.run(explain.explain_run(facts, ScriptedProvider(), "checked"))
    assert result.source == "builtin" and result.rejected


def test_explanation_api(client):  # noqa: F811
    body = {
        "site_id": "tallowmere",
        "task_id": "buy-one",
        "persona_id": "keyboard-only",
        "enforcement": ["gate"],
        "provider": "fake",
    }
    run_id = client.post("/runs", json=body).json()["id"]
    reply = client.get(f"/runs/{run_id}/explanation", params={"mode": "template"}).json()
    assert reply["source"] == "builtin" and reply["headline"]
    assert client.get(f"/runs/{run_id}/explanation", params={"mode": "x"}).status_code == 422
