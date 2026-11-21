"""Planning for batches of runs: resumable and balanced.

The pattern is adapted from Synthetic Users (synthusers/generate.py, plan_next_job and
run_generation; same author, see NOTICE.md):
  - a batch is a set of groups (for example persona x task x enforcement option), each
    with a target number of finished runs;
  - the next run always goes to the group that is furthest behind, so if the model quota
    runs out part-way, the groups that did run are still comparable;
  - progress is read back from the store, so a stopped batch continues where it stopped
    and finished runs are never repeated.

run_batch() is the run controller used by the batch API endpoint and the CLI.
"""

import uuid
from collections.abc import Hashable, Mapping, Sequence
from typing import TypeVar

from vanguard.contracts import (
    BatchGroup,
    BatchRequest,
    BatchStatus,
    EnforcementOption,
    PersonaStatus,
    RunConfig,
    RunOutcome,
    RunStatus,
)

Group = TypeVar("Group", bound=Hashable)


def next_group(done: Mapping[Group, int], targets: Mapping[Group, int]) -> Group | None:
    """The group that should get the next run, or None when every target is met.

    Ties go to the group listed first in `targets`, so the order is deterministic.
    """
    order: Sequence[Group] = list(targets)
    behind = [group for group in order if done.get(group, 0) < targets[group]]
    if not behind:
        return None
    return min(behind, key=lambda group: (done.get(group, 0), order.index(group)))


def remaining(done: Mapping[Group, int], targets: Mapping[Group, int]) -> int:
    return sum(max(0, target - done.get(group, 0)) for group, target in targets.items())


# ---------------------------------------------------------------- running batches


BatchKey = tuple[str, str, tuple[EnforcementOption, ...]]  # task, persona, enforcement


def _options_for(persona_id: str, request: BatchRequest) -> list[list[EnforcementOption]]:
    """Preview personas run only options that enforce nothing (prompt-only, bounded
    perception); their limits are not enforced or checked."""
    from vanguard import catalog
    from vanguard.service import PREVIEW_OPTIONS

    if catalog.persona(persona_id).status is PersonaStatus.PREVIEW:
        allowed = [option for option in request.enforcements if set(option) <= PREVIEW_OPTIONS]
        return allowed or [[EnforcementOption.PROMPT_ONLY]]
    return request.enforcements


def targets_for(request: BatchRequest) -> dict[BatchKey, int]:
    """Every group in the batch, ordered task -> persona -> enforcement."""
    return {
        (task, persona, tuple(option)): request.repeats
        for task in request.task_ids
        for persona in request.persona_ids
        for option in _options_for(persona, request)
    }


def done_counts(store, batch_id: str) -> dict[BatchKey, int]:
    """Finished runs per group, read back from the store (failed runs do not count)."""
    counts: dict[BatchKey, int] = {}
    for run in store.list_runs(batch_id, limit=100_000):
        if run.status is not RunStatus.FINISHED:
            continue
        key = (run.config.task_id, run.config.persona_id, tuple(run.config.enforcement))
        counts[key] = counts.get(key, 0) + 1
    return counts


def status(store, request: BatchRequest, stopped: str | None = None) -> BatchStatus:
    assert request.batch_id is not None
    targets = targets_for(request)
    done = done_counts(store, request.batch_id)
    groups = [
        BatchGroup(
            task_id=task,
            persona_id=persona,
            enforcement=list(option),
            target=target,
            done=min(done.get((task, persona, option), 0), target),
        )
        for (task, persona, option), target in targets.items()
    ]
    return BatchStatus(
        batch_id=request.batch_id,
        groups=groups,
        remaining=remaining(done, targets),
        stopped=stopped,
    )


def prepare(request: BatchRequest, settings) -> BatchRequest:
    """Give the batch an id and validate every group before anything runs."""
    from vanguard import service

    request = request.model_copy(update={"batch_id": request.batch_id or uuid.uuid4().hex[:12]})
    for task, persona, option in targets_for(request):
        service.validate(_config(request, task, persona, option, 0), settings)
    return request


def _config(request: BatchRequest, task, persona, option, repeat: int) -> RunConfig:
    return RunConfig(
        site_id=request.site_id,
        task_id=task,
        persona_id=persona,
        enforcement=list(option),
        provider=request.provider,
        conditions=request.conditions,
        seed=request.seed + repeat,
        repeat_index=repeat,
        max_steps=request.max_steps,
        batch_id=request.batch_id,
    )


MAX_CONSECUTIVE_ERRORS = 3


async def run_batch(request: BatchRequest, settings, store, *, max_runs: int | None = None):
    """Run the batch one run at a time until every group meets its target.

    Safe to call again with the same batch_id: finished runs are counted, not repeated.
    Stops early when the model is unavailable or several runs in a row fail.
    """
    from vanguard import service

    assert request.batch_id is not None
    targets = targets_for(request)
    errors = 0
    started = 0
    while True:
        done = done_counts(store, request.batch_id)
        key = next_group(done, targets)
        if key is None:
            return status(store, request)
        if max_runs is not None and started >= max_runs:
            return status(store, request, "run cap reached")
        task, persona, option = key
        config = _config(request, task, persona, option, done.get(key, 0))
        summary = service.create(config, settings, store)
        started += 1
        result = await service.execute(summary.id, config, settings, store)
        if result.outcome is RunOutcome.ERROR:
            errors += 1
            if (result.error or "").startswith("model unavailable"):
                return status(store, request, result.error)
            if errors >= MAX_CONSECUTIVE_ERRORS:
                return status(store, request, f"{errors} runs in a row failed: {result.error}")
        else:
            errors = 0
