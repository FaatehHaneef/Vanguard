"""HTTP API for the frontend. OpenAPI docs are served at /docs."""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from vanguard import (
    __version__,
    batch,
    catalog,
    explain,
    failures,
    labels,
    results,
    routes,
    service,
)
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
from vanguard.deps import get_store, open_store
from vanguard.providers import ProviderUnavailable, make_provider
from vanguard.settings import Settings, get_settings
from vanguard.store import RunStore


@asynccontextmanager
async def lifespan(app: FastAPI):
    open_store(get_settings())
    yield


app = FastAPI(title="Vanguard API", version=__version__, lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Feature routes (vanguard/routes/*.py), each a module with a `router`.
for _name, _router in routes.routers():
    app.include_router(_router)


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
    background.add_task(service.execute, summary.id, summary.config, settings, store)
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
    media = "image/jpeg" if file.suffix.lower() in (".jpg", ".jpeg") else "image/png"
    return FileResponse(file, media_type=media)


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


@app.get("/labelling/next")
def next_to_label(
    labeller: str,
    count: int = 10,
    batch_id: str | None = None,
    store: RunStore = Depends(get_store),
) -> list[labels.LabelItem]:
    """The next steps this labeller has not labelled, in the shared sample order.
    The checker's verdict is never included."""
    return labels.next_items(store, labeller, min(count, 50), batch_id)


@app.post("/labels", status_code=201)
def save_label(label: labels.Label, store: RunStore = Depends(get_store)) -> labels.Label:
    run = store.get_run(label.run_id)
    if run is None or not 0 <= label.index < run.steps:
        raise HTTPException(404, "step not found")
    if label.verdict is labels.Verdict.YES and label.limit is None:
        raise HTTPException(422, "a 'yes' label needs the limit that was broken")
    labels.save_label(store, label)
    return label


@app.get("/labels")
def list_labels(
    labeller: str | None = None, store: RunStore = Depends(get_store)
) -> list[labels.Label]:
    return labels.labels(store, labeller)


@app.get("/labelling/labellers")
def list_labellers(store: RunStore = Depends(get_store)) -> list[dict]:
    return labels.labellers(store)


@app.get("/labelling/agreement")
def label_agreement(first: str, second: str, store: RunStore = Depends(get_store)) -> dict:
    """Cohen's kappa between two labellers, and checker vs labellers."""
    return labels.agreement(store, first, second)


@app.get("/batches/{batch_id}/failures")
def get_batch_failures(
    batch_id: str,
    settings: Settings = Depends(get_settings),
    store: RunStore = Depends(get_store),
) -> list[dict]:
    """Failing runs grouped by primary cause (tags computed from the records by code)."""
    items = results.batch_failures(store, batch_id, settings)
    return [
        {"cause": cause, "meaning": meaning, "count": count, "runs": [vars(r) for r in runs]}
        for cause, meaning, count, runs in failures.group(items)
    ]


@app.get("/runs/{run_id}/explanation")
async def get_explanation(
    run_id: str,
    mode: str = "checked",
    settings: Settings = Depends(get_settings),
    store: RunStore = Depends(get_store),
) -> explain.Explanation:
    """Plain-language write-up. Facts come from code; the model only words them.
    mode: template (no model), llm (unchecked) or checked (numbers verified)."""
    summary = store.get_run(run_id)
    if summary is None:
        raise HTTPException(404, "run not found")
    if mode not in explain.MODES:
        raise HTTPException(422, f"mode must be one of {', '.join(explain.MODES)}")
    steps = store.steps(run_id)
    leakage, _ = results.score(summary, steps, settings)
    facts = explain.build_facts(
        summary,
        steps,
        leakage,
        catalog.persona(summary.config.persona_id),
        catalog.task(summary.config.task_id),
    )
    provider = None
    if mode != "template":
        try:
            provider = make_provider(settings.default_provider, settings)
        except ProviderUnavailable:
            provider = None
    return await explain.explain_run(facts, provider, mode)
