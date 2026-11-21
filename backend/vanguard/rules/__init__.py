"""Hard leakage rules and safety rules (docs/leakage-spec.md, Section 3).

One implementation serves two callers:
  - the action gate, which checks a proposed action before it runs, and
  - the leakage checker, which re-checks recorded steps after a run.
Sharing the code means the gate and the checker can never disagree about a rule.

Rules are pure functions of (action, persona, context). They never call a model.
"""

from dataclasses import dataclass, field
from enum import StrEnum
from urllib.parse import urljoin, urlsplit

from vanguard.contracts import Action, LimitId, PersonaSpec, Tool, ToolGroup


class ViolationKind(StrEnum):
    ACTION = "action"
    INFORMATION = "information"
    SAFETY = "safety"


@dataclass(frozen=True)
class Violation:
    rule: str  # e.g. "H1"
    limit: LimitId | None  # None for safety rules
    kind: ViolationKind
    message: str  # shown to the agent when blocked, and in reports


@dataclass
class RuleContext:
    """What is known at the moment the action is proposed."""

    current_url: str
    start_url: str
    allowed_origins: list[str]
    seen_links: set[str] = field(default_factory=set)  # absolute URLs seen in any observation
    seen_text: str = ""  # all observation text so far, for H4b (A4)


def _origin(url: str) -> str:
    parts = urlsplit(url)
    return f"{parts.scheme}://{parts.netloc}".lower()


def _normalise(url: str, base: str) -> str:
    absolute = urljoin(base, url)
    parts = urlsplit(absolute)
    path = parts.path.rstrip("/") or "/"
    query = f"?{parts.query}" if parts.query else ""
    return f"{parts.scheme}://{parts.netloc}".lower() + path + query


# ---------------------------------------------------------------- safety


def s0_allowed_origin(action: Action, ctx: RuleContext) -> Violation | None:
    """S0: the browser may only be sent to allowed origins. Always enforced, for every option."""
    if action.tool is not Tool.GOTO or action.url is None:
        return None
    target = _origin(urljoin(ctx.current_url, action.url))
    allowed = {_origin(origin) for origin in ctx.allowed_origins}
    if target in allowed:
        return None
    return Violation("S0", None, ViolationKind.SAFETY, "That address is outside this test.")


# ---------------------------------------------------------------- hard rules


def h1_no_pointer(action: Action, persona: PersonaSpec, ctx: RuleContext) -> Violation | None:
    """H1 (L1): any pointer tool is forbidden."""
    if action.group is ToolGroup.POINTER:
        return Violation(
            "H1",
            LimitId.NO_POINTER,
            ViolationKind.ACTION,
            "This action is not available to this user: they cannot use a mouse or touch.",
        )
    return None


def h4a_unlinked_navigation(
    action: Action, persona: PersonaSpec, ctx: RuleContext
) -> Violation | None:
    """H4a (L4): goto() to a URL that is neither the start URL nor a link seen so far."""
    if action.tool is not Tool.GOTO or action.url is None:
        return None
    target = _normalise(action.url, ctx.current_url)
    known = {_normalise(link, ctx.current_url) for link in ctx.seen_links}
    known.add(_normalise(ctx.start_url, ctx.current_url))
    if target in known:
        return None
    return Violation(
        "H4a",
        LimitId.FIRST_TIME_KNOWLEDGE,
        ViolationKind.INFORMATION,
        "This user has not seen a link to that address, so they cannot know it.",
    )


# Hard rules per limit. H2a/H2b, H3a/H3b, H4b/H4c follow in A4 (see the spec).
HARD_RULES = {
    LimitId.NO_POINTER: [h1_no_pointer],
    LimitId.ACCESSIBILITY_TREE_ONLY: [],
    LimitId.MAGNIFIED_VIEW: [],
    LimitId.FIRST_TIME_KNOWLEDGE: [h4a_unlinked_navigation],
}


def limits_to_check(persona: PersonaSpec) -> list[LimitId]:
    """The control persona is scored against every limit, as if each applied (spec 3.C)."""
    return list(LimitId) if persona.is_control else list(persona.limits)


def hard_violations(action: Action, persona: PersonaSpec, ctx: RuleContext) -> list[Violation]:
    found: list[Violation] = []
    for limit in limits_to_check(persona):
        for rule in HARD_RULES[limit]:
            violation = rule(action, persona, ctx)
            if violation is not None:
                found.append(violation)
    return found
