"""Audit findings and failure attribution (vanguard.findings)."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from vanguard import findings
from vanguard.contracts.findings import FindingsReport
from vanguard.deps import get_settings, get_store
from vanguard.settings import Settings
from vanguard.store import RunStore

router = APIRouter(tags=["findings"])


@router.get("/findings")
def batch_findings(
    batches: Annotated[list[str], Query(description="One or more batch ids")],
    settings: Settings = Depends(get_settings),
    store: RunStore = Depends(get_store),
) -> FindingsReport:
    """Usability findings in these batches, and why each failed run failed."""
    if not any(store.list_runs(batch_id, limit=1) for batch_id in batches):
        raise HTTPException(404, "no runs in these batches")
    return findings.batch_report(store, batches, settings)


@router.get("/runs/{run_id}/findings")
def run_findings(
    run_id: str,
    settings: Settings = Depends(get_settings),
    store: RunStore = Depends(get_store),
) -> FindingsReport:
    report = findings.run_report(store, run_id, settings)
    if report is None:
        raise HTTPException(404, "run not found")
    return report
