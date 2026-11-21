"""The leakage checker: scores recorded steps against the persona's limits after a run.

Proposed owner: Ibrahim (see Vanguard.md, team split). The first version (H1 with
browser evidence, H4a) was written with the foundation; extend it rather than replace it.

What it must do (docs/leakage-spec.md, Sections 1, 3 and 6):
  - For every step, compute *attempted* violations from `step.proposed` using
    vanguard.rules.hard_violations(), the same functions the gate uses, so the gate
    and the checker can never disagree.
  - Compute *executed* violations: attempted violations whose step was executed, plus
    the browser-evidence check for L1: any trusted pointerdown/mousedown/wheel event in
    `step.events` is an executed H1 violation even if the tool name looked harmless.
  - For the control persona, score every limit as if it applied (rules.limits_to_check).
  - Honeytokens (H2b, H3b, H4c) and soft rules (S2-S4) arrive in A4. Soft rules are
    reported separately and never added to hard-rule rates.
  - Never call a model. Leakage is decided by code only.

The shapes below are the contract the metrics, the results page and the labelling
workspace depend on. Do not change them without updating the spec.
"""

from dataclasses import dataclass, field

from vanguard.contracts import LimitId, PersonaSpec, StepRecord
from vanguard.rules import RuleContext, Violation, ViolationKind, hard_violations, limits_to_check

POINTER_EVENTS = frozenset({"pointerdown", "mousedown", "wheel"})

H1_BROWSER = Violation(
    "H1",
    LimitId.NO_POINTER,
    ViolationKind.ACTION,
    "The browser recorded trusted pointer input during this step.",
)


@dataclass
class StepVerdict:
    index: int
    attempted: list[Violation] = field(default_factory=list)
    executed: list[Violation] = field(default_factory=list)


@dataclass
class RunLeakage:
    run_id: str
    steps: list[StepVerdict]

    @property
    def attempted_steps(self) -> int:
        return sum(1 for step in self.steps if step.attempted)

    @property
    def executed_steps(self) -> int:
        return sum(1 for step in self.steps if step.executed)

    def by_limit(self, which: str = "executed") -> dict[LimitId, int]:
        """Steps with at least one violation of each limit ('attempted' or 'executed')."""
        counts: dict[LimitId, int] = {}
        for step in self.steps:
            limits = {v.limit for v in getattr(step, which) if v.limit is not None}
            for limit in limits:
                counts[limit] = counts.get(limit, 0) + 1
        return counts


def pointer_evidence(step: StepRecord) -> bool:
    """True when the browser saw trusted pointer input during the step."""
    return any(event.trusted and event.type in POINTER_EVENTS for event in step.events)


def check_step(
    step: StepRecord,
    persona: PersonaSpec,
    start_url: str,
    seen_links: set[str] | None = None,
) -> StepVerdict:
    """Score one step. `seen_links` holds every link in observations up to and including
    this step; when omitted, only this step's observation counts."""
    verdict = StepVerdict(index=step.index)
    links = set(seen_links) if seen_links is not None else set(step.observation.links)
    if step.proposed is not None:
        ctx = RuleContext(
            current_url=step.observation.url,
            start_url=start_url,
            allowed_origins=[],
            seen_links=links,
        )
        verdict.attempted = hard_violations(step.proposed, persona, ctx)
        if step.executed:
            verdict.executed = list(verdict.attempted)

    if LimitId.NO_POINTER in limits_to_check(persona) and pointer_evidence(step):
        if not any(v.rule == "H1" for v in verdict.executed):
            verdict.executed.append(H1_BROWSER)
        if not any(v.rule == "H1" for v in verdict.attempted):
            verdict.attempted.append(H1_BROWSER)
    return verdict


def check_run(steps: list[StepRecord], persona: PersonaSpec, start_url: str) -> RunLeakage:
    seen: set[str] = set()
    verdicts = []
    for step in sorted(steps, key=lambda s: s.index):
        seen.update(step.observation.links)
        verdicts.append(check_step(step, persona, start_url, seen))
    run_id = steps[0].run_id if steps else ""
    return RunLeakage(run_id=run_id, steps=verdicts)
