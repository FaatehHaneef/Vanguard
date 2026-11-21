"""HTTP API for the frontend. OpenAPI docs are served at /docs."""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from vanguard import __version__, batch, catalog, results, service
from vanguard.agent import PROMPT_VERSION
from vanguard.catalog import CatalogError
from vanguard.contracts import (
    CONTRACT_VERSION,
    BatchRequest,
    BatchStatus,
    PersonaSpec,
    RunConfig,
    RunSummary,
    Site,
    StepRecord,
    Task,
)
from vanguard.settings import Settings, get_settings
from vanguard.store import RunStore

_store: RunStore | None = None


def get_store() -> RunStore:
    if _store is None:
        raise RuntimeError("store not initialised")
    return _store


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _store
    _store = RunStore(get_settings().database_url)
    _store.create_schema()
    yield


app = FastAPI(title="Vanguard API", version=__version__, lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health(settings: Settings = Depends(get_settings)) -> dict:
    return {
        "status": "ok",
        "version": __version__,
        "contracts": CONTRACT_VERSION,
        "prompt": PROMPT_VERSION,
        "executor": settings.executor,
        "providers": settings.enabled_providers,
    }


@app.get("/personas")
def list_personas() -> list[PersonaSpec]:
    return list(catalog.personas().values())


@app.get("/sites")
def list_sites() -> list[Site]:
    return list(catalog.sites().values())


@app.get("/sites/{site_id}/tasks")
def list_tasks(site_id: str) -> list[Task]:
    try:
        catalog.site(site_id)
    except CatalogError as error:
        raise HTTPException(404, str(error)) from None
    return [task for task in catalog.tasks().values() if task.site_id == site_id]


@app.post("/runs", status_code=202)
async def start_run(
    config: RunConfig,
    background: BackgroundTasks,
    settings: Settings = Depends(get_settings),
    store: RunStore = Depends(get_store),
) -> RunSummary:
    try:
        summary = service.create(config, settings, store)
    except (CatalogError, service.RunRejected) as error:
        raise HTTPException(422, str(error)) from None
    background.add_task(service.execute, summary.id, config, settings, store)
    return summary


@app.get("/runs")
def list_runs(
    batch_id: str | None = None, store: RunStore = Depends(get_store)
) -> list[RunSummary]:
    return store.list_runs(batch_id)


@app.get("/runs/{run_id}")
def get_run(run_id: str, store: RunStore = Depends(get_store)) -> RunSummary:
    summary = store.get_run(run_id)
    if summary is None:
        raise HTTPException(404, "run not found")
    return summary


@app.get("/runs/{run_id}/steps")
def get_steps(run_id: str, store: RunStore = Depends(get_store)) -> list[StepRecord]:
    if store.get_run(run_id) is None:
        raise HTTPException(404, "run not found")
    return store.steps(run_id)


@app.get("/runs/{run_id}/report")
def get_report(
    run_id: str,
    settings: Settings = Depends(get_settings),
    store: RunStore = Depends(get_store),
) -> dict:
    """Metrics and per-step leakage verdicts, computed by code from the stored steps."""
    report = results.run_report(store, run_id, settings)
    if report is None:
        raise HTTPException(404, "run not found")
    return report


@app.get("/runs/{run_id}/steps/{index}/screenshot")
def get_screenshot(
    run_id: str,
    index: int,
    settings: Settings = Depends(get_settings),
    store: RunStore = Depends(get_store),
) -> FileResponse:
    steps = [step for step in store.steps(run_id) if step.index == index]
    path = steps[0].observation.screenshot_path if steps else None
    if not path:
        raise HTTPException(404, "no screenshot for this step")
    file = Path(path).resolve()
    root = (Path(settings.data_dir) / "screenshots").resolve()
    if not file.is_relative_to(root) or not file.is_file():
        raise HTTPException(404, "no screenshot for this step")
    return FileResponse(file, media_type="image/png")


@app.get("/batches/{batch_id}/metrics")
def get_batch_metrics(
    batch_id: str,
    settings: Settings = Depends(get_settings),
    store: RunStore = Depends(get_store),
) -> list[dict]:
    """Metrics per persona x task x enforcement x provider group in one batch."""
    return [group.as_dict() for group in results.batch_groups(store, batch_id, settings)]


@app.post("/batches", status_code=202)
async def start_batch(
    request: BatchRequest,
    background: BackgroundTasks,
    settings: Settings = Depends(get_settings),
    store: RunStore = Depends(get_store),
) -> BatchStatus:
    """Queue a balanced batch. Posting the same batch_id again continues it."""
    try:
        request = batch.prepare(request, settings)
    except (CatalogError, service.RunRejected) as error:
        raise HTTPException(422, str(error)) from None
    store.save_batch(request)
    background.add_task(batch.run_batch, request, settings, store)
    return batch.status(store, request)


@app.get("/batches")
def list_batches(store: RunStore = Depends(get_store)) -> list[BatchStatus]:
    return [batch.status(store, request) for request in store.list_batches()]


@app.get("/batches/{batch_id}")
def get_batch(batch_id: str, store: RunStore = Depends(get_store)) -> BatchStatus:
    request = store.get_batch(batch_id)
    if request is None:
        raise HTTPException(404, "batch not found")
    return batch.status(store, request)
