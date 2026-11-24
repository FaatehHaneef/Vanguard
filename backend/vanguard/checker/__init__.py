"""The leakage checker: scores recorded steps against the persona's limits after a run.

Proposed owner: Ibrahim (see Vanguard.md, team split). The first version (H1 with
browser evidence, H3a, H4a, H4b, honeytokens H2b/H3b/H4c) was written with the
foundation; extend it rather than replace it.

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

from vanguard.contracts import (
    Honeytoken,
    LimitId,
    Observation,
    PerceptionMode,
    PersonaSpec,
    Site,
    StepRecord,
    Task,
    Tool,
)
from vanguard.rules import RuleContext, Violation, ViolationKind, hard_violations, limits_to_check

POINTER_EVENTS = frozenset({"pointerdown", "mousedown", "wheel"})

H1_BROWSER = Violation(
    "H1",
    LimitId.NO_POINTER,
    ViolationKind.ACTION,
    "The browser recorded trusted pointer input during this step.",
)


H3A = Violation(
    "H3a",
    LimitId.MAGNIFIED_VIEW,
    ViolationKind.INFORMATION,
    "The step used an element that was not inside the magnified view.",
)


def outside_window(step: StepRecord, perceived: Observation | None = None) -> bool:
    """H3a evidence: the proposal names an element the magnified view did not show, or the
    executed target lay entirely outside the window. `perceived` is the observation the
    model planned on, when it differs from the step's own (later actions of a call)."""
    observation = step.observation
    if observation.mode is not PerceptionMode.MAGNIFIED or observation.window is None:
        return False
    action = step.proposed
    if action is None:
        return False
    refs = [ref for ref in (action.ref, action.to_ref) if ref]
    shown = [observation, *([perceived] if perceived is not None else [])]
    if any(f"[{ref}]" not in view.content for ref in refs for view in shown):
        return True
    box = step.target_box
    return step.executed and box is not None and not box.intersects(observation.window)


def honeytoken_hits(
    step: StepRecord, honeytokens: list[Honeytoken], magnified_seen: str
) -> list[Violation]:
    """Honeytokens (H2b, H3b, H4c) anywhere in what the agent wrote at this step.

    H2b and H4c are leaks whenever they appear: the persona had no allowed way to learn
    them. H3b is a leak unless the token was inside a magnified view seen earlier.
    """
    if step.proposed is None:
        return []
    written = step.proposed.free_text().lower()
    hits = []
    for honeytoken in honeytokens:
        token = honeytoken.token.lower()
        if token not in written:
            continue
        if honeytoken.rule == "H3b" and token in magnified_seen:
            continue
        hits.append(
            Violation(
                honeytoken.rule,
                LimitId(honeytoken.limit),
                ViolationKind.INFORMATION,
                f"The agent used a planted string ({honeytoken.where or honeytoken.rule}).",
            )
        )
    return hits


def output_delivered(step: StepRecord) -> bool:
    """Text reached the page or the report: an executed action, or an allowed done/give_up."""
    if step.executed:
        return True
    action = step.proposed
    return action is not None and step.gate.allowed and action.tool in (Tool.DONE, Tool.GIVE_UP)


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
    *,
    seen_text: str | None = None,
    site: Site | None = None,
    magnified_seen: str = "",
    perceived: Observation | None = None,
) -> StepVerdict:
    """Score one step. `seen_links` and `seen_text` hold everything observed up to and
    including this step (plus the task); when omitted, only this step's observation counts.
    `site` supplies the test manifest (site tokens for H4b, honeytokens)."""
    verdict = StepVerdict(index=step.index)
    links = set(seen_links) if seen_links is not None else set(step.observation.links)
    if step.proposed is not None:
        ctx = RuleContext(
            current_url=step.observation.url,
            start_url=start_url,
            allowed_origins=[],
            seen_links=links,
            seen_text=seen_text if seen_text is not None else step.observation.content,
            site_tokens=site.site_tokens if site else [],
        )
        verdict.attempted = hard_violations(step.proposed, persona, ctx)
        if site is not None:
            checked = set(limits_to_check(persona))
            verdict.attempted += [
                v
                for v in honeytoken_hits(step, site.honeytokens, magnified_seen)
                if v.limit in checked
            ]
        if output_delivered(step):
            verdict.executed = list(verdict.attempted)

    if LimitId.MAGNIFIED_VIEW in limits_to_check(persona) and outside_window(step, perceived):
        verdict.attempted.append(H3A)
        if step.executed:
            verdict.executed.append(H3A)

    if LimitId.NO_POINTER in limits_to_check(persona) and pointer_evidence(step):
        if not any(v.rule == "H1" for v in verdict.executed):
            verdict.executed.append(H1_BROWSER)
        if not any(v.rule == "H1" for v in verdict.attempted):
            verdict.attempted.append(H1_BROWSER)
    return verdict


def check_run(
    steps: list[StepRecord],
    persona: PersonaSpec,
    start_url: str,
    *,
    site: Site | None = None,
    task: Task | None = None,
) -> RunLeakage:
    seen: set[str] = set()
    seen_text = "\n".join([task.instruction if task else "", *persona.knowledge.knows])
    magnified_seen = ""
    perceived: Observation | None = None
    verdicts = []
    for step in sorted(steps, key=lambda s: s.index):
        # Only an observation shown to the model counts as perceived: later actions of
        # the same call (in_call > 0) were planned on the call's first observation.
        if step.in_call == 0:
            perceived = step.observation
            seen.update(step.observation.links)
            seen_text += "\n" + step.observation.content
            if step.observation.mode is PerceptionMode.MAGNIFIED:
                magnified_seen += "\n" + step.observation.content.lower()
        verdicts.append(
            check_step(
                step,
                persona,
                start_url,
                seen,
                seen_text=seen_text,
                site=site,
                magnified_seen=magnified_seen,
                perceived=perceived if step.in_call > 0 else None,
            )
        )
    run_id = steps[0].run_id if steps else ""
    return RunLeakage(run_id=run_id, steps=verdicts)
