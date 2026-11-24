"""Realism (vanguard.evaluation.realism): persona input profiles vs a fake A11y-CUA folder."""

import json

import pytest
from test_evaluation_tasks import (  # noqa: F401  (fixture)
    CHEAPEST,
    KEYS,
    SETTINGS,
    click,
    scored,
    scripted_run,
    store,
)

from vanguard.contracts import Action, EnforcementOption
from vanguard.evaluation import realism
from vanguard.evaluation.__main__ import main
from vanguard.reference.a11y_cua import collect


def fake_reference(root):
    def write(rel, records):
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(records), encoding="utf-8")

    # Blind and low-vision users: 4 key presses (2 Tab, 1 Enter), 1 hotkey, no pointer.
    write(
        "BLVU/BLVU1/1/1_chrome.exe.json",
        [
            {"event": {"type": "key_press", "key": "Tab"}},
            {"event": {"type": "key_press", "key": "Tab"}},
            {"event": {"type": "key_press", "key": "Enter"}},
            {"event": {"type": "key_press", "key": "a"}},
            {"event": {"type": "hotkey", "key": "Ctrl"}},
        ],
    )
    # Sighted users: 3 clicks, 1 scroll, 1 key press (Enter), cursor moves left out.
    write(
        "SU/SU1/1/1_chrome.exe.json",
        [
            {"event": "mouse_click"},
            {"event": "mouse_click"},
            {"event": "mouse_click"},
            {"event": "scroll"},
            {"event": "mouse_move"},
            {"event": {"type": "key_press", "key": "Return"}},
        ],
    )
    return collect(root)


def test_persona_profile_counts_presses_repeats_and_typing(store):  # noqa: F811
    tab3 = Action(tool="press", key="Tab", repeat=3)
    typed = Action(tool="type", text="Sara")
    goto = Action(tool="goto", url="/")
    scripted_run(store, [tab3, typed, goto, *KEYS])
    (profile,) = realism.persona_profiles(scored(store)).values()
    # 3 + 4 Tab presses, 4 typed characters, 4 Enter presses; goto is not input.
    assert profile.key_presses == 3 + 4 + 4 + 4
    assert profile.tab_and_arrows == 7
    assert profile.enter == 4
    assert profile.pointer == 0 and profile.pointer_share == 0.0


def test_only_executed_actions_count(store):  # noqa: F811
    # Under the gate the keyboard-only persona's click is refused, so it never executes.
    scripted_run(store, [click, *KEYS], enforcement=EnforcementOption.GATE)
    scripted_run(store, [click, *KEYS], enforcement=EnforcementOption.PROMPT_ONLY, batch="b2")
    gated = realism.persona_profiles(scored(store, "b1"))["keyboard-only"]
    loose = realism.persona_profiles(scored(store, "b2"))["keyboard-only"]
    assert gated.pointer == 0
    assert loose.pointer == 1
    # The click ran (it followed the first link), so the route needed fewer key presses.
    assert 0 < loose.key_presses < 8
    assert loose.pointer_share == pytest.approx(1 / (1 + loose.key_presses))


def test_reference_profile_uses_the_same_definitions(tmp_path):
    reference = fake_reference(tmp_path)
    blind = realism.reference_profile(reference["Blind and low-vision users"])
    assert (blind.key_presses, blind.pointer) == (5, 0)  # 4 presses + 1 hotkey
    assert blind.tab_and_arrow_share == pytest.approx(2 / 5)
    assert blind.enter_share == pytest.approx(1 / 5)
    sighted = realism.reference_profile(reference["Sighted users"])
    assert sighted.pointer_share == pytest.approx(4 / 5)
    assert sighted.enter_share == 1.0  # "Return" counts as Enter


def test_comparison_pairs_personas_with_their_groups(store, tmp_path):  # noqa: F811
    scripted_run(store, KEYS)
    scripted_run(store, [click, CHEAPEST], persona="unrestricted", task="cheapest")
    scripted_run(store, [CHEAPEST], persona="first-time", task="cheapest")
    found = {c.persona_id: c for c in realism.compare(scored(store), fake_reference(tmp_path))}
    assert found["keyboard-only"].group == "Blind and low-vision users"
    assert found["unrestricted"].group == "Sighted users"
    assert found["first-time"].group is None and found["first-time"].differences() is None
    keyboard = found["keyboard-only"].differences()
    # Persona: 4 Tab, 4 Enter of 8 presses; users: 2/5 Tab and arrows, 1/5 Enter.
    assert keyboard["tab_and_arrow_share"] == pytest.approx(abs(0.5 - 0.4))
    assert keyboard["enter_share"] == pytest.approx(abs(0.5 - 0.2))
    assert keyboard["pointer_share"] == 0.0
    sighted = found["unrestricted"].differences()
    assert sighted["pointer_share"] == pytest.approx(abs(1.0 - 0.8))


def test_report_shows_values_side_by_side(store, tmp_path):  # noqa: F811
    scripted_run(store, KEYS)
    comparisons = realism.compare(scored(store), fake_reference(tmp_path))
    text = realism.report(comparisons, ["b1"], reference_found=True)
    assert "| keyboard-only | 1 | Blind and low-vision users | 0.0% / 0.0% / 0.0% |" in text
    assert "50.0% / 40.0% / 10.0%" in text
    assert "desktop tasks" in text
    missing = realism.report(realism.compare(scored(store), {}), ["b1"], reference_found=False)
    assert "was not found" in missing and "0.0% / - / -" in missing


def test_realism_command_writes_the_file(store, tmp_path, monkeypatch):  # noqa: F811
    scripted_run(store, KEYS, batch="suite")
    fake_reference(tmp_path / "ref")
    monkeypatch.setattr("vanguard.evaluation.realism.open_store", lambda: (store, SETTINGS))
    out = tmp_path / "realism.md"
    args = [
        "realism",
        "--batches",
        "suite",
        "--reference",
        str(tmp_path / "ref"),
        "--out",
        str(out),
    ]
    assert main(args) == 0
    assert "Blind and low-vision users" in out.read_text(encoding="utf-8")
