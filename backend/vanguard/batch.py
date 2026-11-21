"""Planning for batches of runs: resumable and balanced.

The pattern is adapted from Synthetic Users (synthusers/generate.py, plan_next_job and
run_generation; same author, see NOTICE.md):
  - a batch is a set of groups (for example persona x task x enforcement option), each
    with a target number of finished runs;
  - the next run always goes to the group that is furthest behind, so if the model quota
    runs out part-way, the groups that did run are still comparable;
  - progress is read back from the store, so a stopped batch continues where it stopped
    and finished runs are never repeated.

The run controller (batch API endpoint and worker queue) builds on next_group().
"""

from collections.abc import Hashable, Mapping, Sequence
from typing import TypeVar

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
