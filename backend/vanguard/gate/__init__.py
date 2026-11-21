"""The action gate: decides whether a proposed action may reach the browser.

Two layers:
  1. Safety rules (S0) are always enforced, whatever enforcement option is chosen.
     The agent can never send the browser outside the allowed origins.
  2. Hard leakage rules are enforced only when the run uses the GATE option, and only
     for the persona's own limits. The control persona is never blocked for leakage:
     its violations are recorded as attempted leakage by the checker instead.

When an action is blocked the agent is told why, in words it can act on, and the
step is recorded with the rule id.
"""

from vanguard.contracts import Action, EnforcementOption, GateDecision, PersonaSpec
from vanguard.rules import RuleContext, hard_violations, s0_allowed_origin


class ActionGate:
    def __init__(self, persona: PersonaSpec, enforcement: list[EnforcementOption]):
        self.persona = persona
        self.enforce_limits = EnforcementOption.GATE in enforcement and not persona.is_control

    def decide(self, action: Action, ctx: RuleContext) -> GateDecision:
        safety = s0_allowed_origin(action, ctx)
        if safety is not None:
            return GateDecision(allowed=False, rule=safety.rule, message=safety.message)

        if self.enforce_limits:
            violations = hard_violations(action, self.persona, ctx)
            if violations:
                first = violations[0]
                return GateDecision(allowed=False, rule=first.rule, message=first.message)

        return GateDecision(allowed=True)
