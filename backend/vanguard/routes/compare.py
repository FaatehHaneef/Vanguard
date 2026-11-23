"""GET /compare: two batches side by side, group by group (vanguard.compare)."""

from fastapi import APIRouter, Depends, HTTPException

from vanguard import compare as comparing
from vanguard.contracts.compare import CompareMatch, Comparison
from vanguard.deps import get_settings, get_store
from vanguard.settings import Settings
from vanguard.store import RunStore

router = APIRouter(tags=["compare"])


@router.get("/compare")
def compare_batches(
    baseline: str,
    candidate: str,
    match: CompareMatch = CompareMatch.FULL,
    settings: Settings = Depends(get_settings),
    store: RunStore = Depends(get_store),
) -> Comparison:
    """Per group: baseline and candidate metrics, the change in each (better, worse,
    same), plus failure causes that are new in the candidate or gone from it."""
    for batch_id in (baseline, candidate):
        if not store.list_runs(batch_id, limit=1):
            raise HTTPException(404, f"no runs in batch {batch_id}")
    return comparing.compare(store, baseline, candidate, settings, match)
