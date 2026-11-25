"""Diversity (vanguard.evaluation.diversity) over scripted runs on the fake shop."""

import pytest
from test_evaluation_tasks import (  # noqa: F401  (fixture)
    CHEAPEST,
    KEYS,
    SETTINGS,
    enter,
    escape,
    scored,
    scripted_run,
    store,
    tab,
)

from vanguard.contracts import Action, EnforcementOption
from vanguard.evaluation import diversity
from vanguard.evaluation.__main__ import main


def test_edit_distance_and_normalisation():
    assert diversity.edit_distance([], []) == 0
    assert diversity.edit_distance(["a", "b", "c"], ["a", "c"]) == 1
    assert diversity.edit_distance(["a", "b"], ["b", "a"]) == 2
    assert diversity.normalised_distance([], []) == 0.0
    assert diversity.normalised_distance(["a", "b"], ["a", "b"]) == 0.0
    assert diversity.normalised_distance(["a", "b"], ["c", "d"]) == 1.0
    assert diversity.normalised_distance(["a", "b", "c", "d"], ["a", "b"]) == 0.5


def test_action_types_keep_the_key_of_a_press():
    assert diversity.action_type(tab) == "press Tab"
    assert diversity.action_type(Action(tool="click", ref="e1")) == "click"
    assert diversity.action_type(CHEAPEST) == "done"


def test_identical_runs_have_no_diversity_within_a_persona(store):  # noqa: F811
    for _ in range(3):
        scripted_run(store, KEYS)
    d = diversity.measure(scored(store))
    assert d.within[("buy-one", "keyboard-only")] == 0.0
    assert d.actions["keyboard-only"].std == 0.0 and d.actions["keyboard-only"].iqr == 0.0
    assert d.completion["keyboard-only"].mean == 1.0
    (only_path,) = d.paths[("buy-one", "keyboard-only")]
    assert d.paths[("buy-one", "keyboard-only")][only_path] == 3
    assert only_path[0] == "/" and only_path[-1].startswith("/thanks/")


def test_different_runs_are_measured_pairwise(store):  # noqa: F811
    scripted_run(store, KEYS)  # 8 actions
    scripted_run(store, [escape, *KEYS])  # 9 actions, one inserted
    d = diversity.measure(scored(store))
    assert d.within[("buy-one", "keyboard-only")] == pytest.approx(1 / 9)
    assert d.actions["keyboard-only"].mean == 8.5
    assert d.actions["keyboard-only"].std == pytest.approx(0.5)


def test_a_single_run_has_no_within_distance(store):  # noqa: F811
    scripted_run(store, KEYS)
    assert diversity.measure(scored(store)).within[("buy-one", "keyboard-only")] is None


def test_between_personas_on_the_same_task(store):  # noqa: F811
    scripted_run(store, [CHEAPEST], task="cheapest")
    scripted_run(store, [CHEAPEST], task="cheapest", persona="unrestricted")
    # Prompt-only: under the gate H4b would refuse the first-time visitor's unseen answer.
    scripted_run(
        store,
        [tab, CHEAPEST],
        task="cheapest",
        persona="first-time",
        enforcement=EnforcementOption.PROMPT_ONLY,
    )
    d = diversity.measure(scored(store))
    assert d.between[("cheapest", "keyboard-only", "unrestricted")] == 0.0
    assert d.between[("cheapest", "first-time", "keyboard-only")] == pytest.approx(0.5)
    assert len(d.between) == 3


def test_entropy_of_the_action_mix(store):  # noqa: F811
    scripted_run(store, [tab, enter] * 4)  # equal Tab and Enter: 1 bit
    scripted_run(store, [CHEAPEST], task="cheapest", persona="unrestricted")
    d = diversity.measure(scored(store))
    bits, kinds, actions = d.entropy["keyboard-only"]
    assert (bits, kinds, actions) == (pytest.approx(1.0), 2, 8)
    assert d.entropy["unrestricted"] == (0.0, 1, 1)


def test_spread_across_personas(store):  # noqa: F811
    scripted_run(store, KEYS)  # success
    scripted_run(store, [Action(tool="give_up", reason="lost")], persona="unrestricted")
    d = diversity.measure(scored(store))
    assert d.across_completion.mean == 0.5
    assert d.across_completion.std == pytest.approx(0.5)
    assert d.completion["unrestricted"].mean == 0.0


def test_report_and_command(store, tmp_path, monkeypatch):  # noqa: F811
    scripted_run(store, KEYS, batch="suite")
    scripted_run(store, [escape, *KEYS], batch="suite")
    d = diversity.measure(scored(store, "suite"))
    text = diversity.report(d, ["suite"], runs=2)
    for heading in ("(a) Edit distance within", "(b) Entropy", "(c) Spread", "(d) Distinct"):
        assert heading in text
    assert "| `buy-one` | keyboard-only | 0.11 |" in text
    assert "No task was run by more than one persona." in text
    assert "No finished runs" in diversity.report(diversity.measure([]), ["x"], runs=0)
    monkeypatch.setattr("vanguard.evaluation.diversity.open_store", lambda: (store, SETTINGS))
    out = tmp_path / "diversity.md"
    assert main(["diversity", "--batches", "suite", "--out", str(out)]) == 0
    assert "| keyboard-only |" in out.read_text(encoding="utf-8")
