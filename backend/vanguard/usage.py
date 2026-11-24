"""Model calls made from this machine's store, for staying inside the free-tier quota.

    python -m vanguard.cli usage            # today's calls against today's budget

Gemini's free-tier quota is per key, per model and per day, and the day resets at
midnight Pacific time. A call is one agent proposal (the first step of each call, so
several actions from one call count once) plus one verifier check for every step the
verifier judged. Explanations in llm or checked mode are not stored as steps and are not
counted; keep them for the deployed app, not the batch days.
"""

from collections import Counter
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from zoneinfo import ZoneInfo

from vanguard.contracts import StepRecord
from vanguard.settings import Settings
from vanguard.store import RunStore

QUOTA_ZONE = ZoneInfo("America/Los_Angeles")


def quota_day_start(now: datetime | None = None) -> datetime:
    """The start of the current quota day (midnight Pacific), in UTC."""
    local = (now or datetime.now(UTC)).astimezone(QUOTA_ZONE)
    midnight = local.replace(hour=0, minute=0, second=0, microsecond=0)
    return midnight.astimezone(UTC)


def calls_in(steps: list[StepRecord]) -> int:
    """Model calls behind these steps: agent calls plus verifier checks."""
    return sum(step.model_call for step in steps) + sum(step.verifier is not None for step in steps)


@dataclass
class Usage:
    since: datetime
    agent_calls: int = 0
    verifier_calls: int = 0
    runs: int = 0
    by_model: Counter = field(default_factory=Counter)

    @property
    def calls(self) -> int:
        return self.agent_calls + self.verifier_calls


def _aware(moment: datetime) -> datetime:
    return moment if moment.tzinfo else moment.replace(tzinfo=UTC)


def usage_since(store: RunStore, since: datetime) -> Usage:
    found = Usage(since=since)
    # A run can start before the day began and go on after it, so look a day back.
    for run in store.list_runs(limit=100_000):
        if _aware(run.created_at) < since - timedelta(days=1):
            continue
        steps = [step for step in store.steps(run.id) if _aware(step.started_at) >= since]
        if not steps:
            continue
        found.runs += 1
        for step in steps:
            if step.model_call:
                found.agent_calls += 1
                found.by_model[step.model or "unknown"] += 1
            if step.verifier is not None:
                found.verifier_calls += 1
                found.by_model[step.model or "unknown"] += 1
    return found


def daily_budget(settings: Settings) -> int:
    """Calls per model per day across the configured keys."""
    return len(settings.gemini_api_keys) * settings.calls_per_key_per_day


def left_today(store: RunStore, settings: Settings) -> int:
    return max(0, daily_budget(settings) - usage_since(store, quota_day_start()).calls)


def report(found: Usage, settings: Settings) -> str:
    budget = daily_budget(settings)
    keys, per_key = len(settings.gemini_api_keys), settings.calls_per_key_per_day
    local = found.since.astimezone()
    lines = [
        f"Quota day since {local:%Y-%m-%d %H:%M} local time (midnight Pacific)",
        f"  model calls: {found.calls} ({found.agent_calls} agent, "
        f"{found.verifier_calls} verifier) in {found.runs} runs",
    ]
    for model, count in sorted(found.by_model.items()):
        lines.append(f"  {model}: {count}")
    if budget:
        left = max(0, budget - found.calls)
        lines.append(f"  budget: {budget} ({keys} keys x {per_key}); left today: {left}")
        lines.append(f"  next batch: --max-calls {left}")
    else:
        lines.append("  budget: no Gemini keys configured")
    return "\n".join(lines)
