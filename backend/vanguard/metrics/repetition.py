"""Repeated attempts: proposals that try the same thing again without effect.

A step counts as a repeated attempt when its proposal is the same as the previous
step's proposal (same tool and the same key, ref, text and URL) and either
  - the gate refused the previous one, so the agent is retrying a refused action; or
  - the previous one changed nothing: the URL and the focus after it were the same as
    before it.
A step is counted once even if both hold. Steps without a valid proposal never count,
and they break a run of repeats.
"""

from vanguard.contracts import Action, StepRecord

Signature = tuple[str, str | None, str | None, str | None, str | None]


def signature(action: Action) -> Signature:
    """What makes two proposals 'the same': the tool and its target or input."""
    return (str(action.tool), action.key, action.ref, action.text, action.url)


def _changed_nothing(step: StepRecord, focus_before: str | None) -> bool:
    url_before = step.observation.url
    url_after = step.url_after or url_before
    return url_after == url_before and step.focus_after == focus_before


def repeated_attempts(steps: list[StepRecord]) -> int:
    """The number of repeated attempts in one run's steps (in step order)."""
    ordered = sorted(steps, key=lambda step: step.index)
    count = 0
    for position in range(1, len(ordered)):
        previous, current = ordered[position - 1], ordered[position]
        if previous.proposed is None or current.proposed is None:
            continue
        if signature(previous.proposed) != signature(current.proposed):
            continue
        focus_before = ordered[position - 2].focus_after if position >= 2 else None
        if not previous.gate.allowed or _changed_nothing(previous, focus_before):
            count += 1
    return count
