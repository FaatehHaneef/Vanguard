import pytest
from pydantic import ValidationError

from vanguard import catalog
from vanguard.contracts import Action, EnforcementOption
from vanguard.gate import ActionGate
from vanguard.rules import RuleContext, hard_violations

ORIGIN = "http://localhost:3100"


def ctx(**overrides) -> RuleContext:
    base = dict(
        current_url=f"{ORIGIN}/",
        start_url=f"{ORIGIN}/",
        allowed_origins=[ORIGIN],
        seen_links={f"{ORIGIN}/product/dusk-ember"},
    )
    base.update(overrides)
    return RuleContext(**base)


keyboard = catalog.persona("keyboard-only")
control = catalog.persona("unrestricted")
click = Action(tool="click", ref="e12", rationale="press add to cart")
tab = Action(tool="press", key="Tab")


def test_action_needs_its_arguments():
    with pytest.raises(ValidationError):
        Action(tool="click")
    with pytest.raises(ValidationError):
        Action(tool="sr_next", kind="paragraph")


def test_h1_flags_pointer_for_keyboard_persona():
    assert [v.rule for v in hard_violations(click, keyboard, ctx())] == ["H1"]
    assert hard_violations(tab, keyboard, ctx()) == []


def test_control_is_scored_against_every_limit():
    unlinked = Action(tool="goto", url="/checkout")
    rules = {v.rule for v in hard_violations(click, control, ctx())}
    rules |= {v.rule for v in hard_violations(unlinked, control, ctx())}
    assert rules == {"H1", "H4a"}


def test_h4a_allows_seen_links_and_start_url():
    first_time = catalog.persona("first-time")
    assert hard_violations(Action(tool="goto", url="/product/dusk-ember/"), first_time, ctx()) == []
    assert hard_violations(Action(tool="goto", url="/"), first_time, ctx()) == []
    flagged = hard_violations(Action(tool="goto", url="/checkout"), first_time, ctx())
    assert [v.rule for v in flagged] == ["H4a"]


def test_gate_blocks_pointer_only_with_gate_option():
    gated = ActionGate(keyboard, [EnforcementOption.GATE])
    prompt_only = ActionGate(keyboard, [EnforcementOption.PROMPT_ONLY])
    assert gated.decide(click, ctx()).rule == "H1"
    assert prompt_only.decide(click, ctx()).allowed


def test_gate_never_blocks_control_for_leakage():
    gate = ActionGate(control, [EnforcementOption.GATE])
    assert gate.decide(click, ctx()).allowed


@pytest.mark.parametrize(
    "url",
    ["https://www.paypal.com/checkoutnow", "https://evil.example/", "//api.braintreegateway.com/x"],
)
def test_safety_rule_blocks_other_origins_for_every_option(url):
    for option in EnforcementOption:
        decision = ActionGate(control, [option]).decide(Action(tool="goto", url=url), ctx())
        assert not decision.allowed and decision.rule == "S0"


def test_gate_blocks_h4b_for_first_time_visitor_only_with_gate():
    first_time = catalog.persona("first-time")
    typed = Action(tool="type", text="Lantern Honey")
    context = ctx(site_tokens=["Lantern Honey"], seen_text="Buy a candle")
    assert ActionGate(first_time, [EnforcementOption.GATE]).decide(typed, context).rule == "H4b"
    seen = ctx(site_tokens=["Lantern Honey"], seen_text="Lantern Honey $22.00")
    assert ActionGate(first_time, [EnforcementOption.GATE]).decide(typed, seen).allowed
