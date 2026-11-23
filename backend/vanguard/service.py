"""Starting runs: wires the catalog, provider, executor, gate and store together.

For A3, runs execute in the API process as background tasks. The worker service in
Docker Compose takes this over when runs move to a queue.
"""

from vanguard import catalog, origins
from vanguard.agent import run_once
from vanguard.contracts import EnforcementOption, PersonaStatus, RunConfig, RunSummary
from vanguard.executor import Executor, FakeExecutor
from vanguard.providers import make_provider
from vanguard.settings import Settings
from vanguard.store import RunStore


class RunRejected(ValueError):
    pass


# Preview personas: nothing is enforced on their actions or checked, but their
# perception can be bounded (option 3).
PREVIEW_OPTIONS = {EnforcementOption.PROMPT_ONLY, EnforcementOption.BOUNDED_PERCEPTION}


def make_executor(settings: Settings, config: RunConfig | None = None) -> Executor:
    if settings.executor == "fake":
        return FakeExecutor()
    if settings.executor == "playwright":
        from vanguard.executor.playwright import PlaywrightExecutor  # added with the worker

        return PlaywrightExecutor(
            settings,
            conditions=config.conditions if config else None,
            bounded_perception=bool(
                config and EnforcementOption.BOUNDED_PERCEPTION in config.enforcement
            ),
        )
    raise RunRejected(f"Unknown executor {settings.executor!r}")


def validate(config: RunConfig, settings: Settings) -> None:
    persona = catalog.persona(config.persona_id)
    task = catalog.task(config.task_id)
    if task.site_id != config.site_id:
        raise RunRejected(f"Task {task.id} does not belong to site {config.site_id}")
    catalog.site(config.site_id)
    if persona.status is PersonaStatus.PREVIEW and not set(config.enforcement) <= PREVIEW_OPTIONS:
        raise RunRejected(
            f"{persona.name} is a preview persona: only prompt_only and bounded_perception"
            " runs are available"
        )
    if config.provider not in settings.enabled_providers:
        raise RunRejected(f"Provider {config.provider!r} is not enabled here")


def create(config: RunConfig, settings: Settings, store: RunStore) -> RunSummary:
    validate(config, settings)
    return store.create_run(config)


async def execute(
    run_id: str, config: RunConfig, settings: Settings, store: RunStore
) -> RunSummary:
    site = catalog.site(config.site_id)
    return await run_once(
        run_id,
        config,
        catalog.persona(config.persona_id),
        site,
        catalog.task(config.task_id),
        make_provider(config.provider, settings),
        make_executor(settings, config),
        store,
        allowed_origins=origins.allowed_origins(settings),
        max_steps=config.max_steps or settings.max_steps_per_run,
        stuck_after=settings.stuck_after_steps,
    )
