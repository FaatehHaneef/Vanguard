"""HTTP API for the frontend. OpenAPI docs are served at /docs."""

from contextlib import asynccontextmanager

from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from vanguard import __version__, catalog, service
from vanguard.agent import PROMPT_VERSION
from vanguard.catalog import CatalogError
from vanguard.contracts import CONTRACT_VERSION, PersonaSpec, RunConfig, RunSummary, Site, StepRecord, Task
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
def list_runs(batch_id: str | None = None, store: RunStore = Depends(get_store)) -> list[RunSummary]:
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
