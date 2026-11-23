"""Personas, sites and tasks: the built-in catalog plus custom items from the studio.

Built-in items are JSON files in ./data, so non-programmers can read and review them:
  - data/personas/<id>.json: one persona each;
  - data/sites/<site-id>.json: one site with its tasks ({"site": {...}, "tasks": [...]}),
    so each site's owner edits only their own file;
  - data/tasks/*.json: extra tasks on any site ({"tasks": [...]}), for example a task suite.
Every file is validated against the contracts when it is loaded.

Custom items (made in the configuration studio and stored in the database) come from the
module `vanguard.studio.source` when it exists: functions personas(), sites() and
tasks(), each returning a dict by id. They are read fresh on every call, so edits appear
at once. A custom item never replaces a built-in one with the same id.
"""

import importlib
import importlib.util
import json
from functools import lru_cache
from pathlib import Path

from vanguard.contracts import PersonaSpec, Site, Task

DATA = Path(__file__).parent / "data"
STUDIO_SOURCE = "vanguard.studio.source"


class CatalogError(LookupError):
    pass


# ---------------------------------------------------------------- built-in items


@lru_cache
def builtin_personas() -> dict[str, PersonaSpec]:
    specs = [
        PersonaSpec.model_validate_json(path.read_text(encoding="utf-8"))
        for path in sorted((DATA / "personas").glob("*.json"))
    ]
    return {spec.id: spec for spec in specs}


@lru_cache
def _site_files() -> tuple[dict, ...]:
    return tuple(
        json.loads(path.read_text(encoding="utf-8"))
        for path in sorted((DATA / "sites").glob("*.json"))
    )


@lru_cache
def builtin_sites() -> dict[str, Site]:
    found: dict[str, Site] = {}
    for entry in _site_files():
        site = Site.model_validate(entry["site"])
        if site.id in found:
            raise CatalogError(f"Site {site.id} is defined twice")
        found[site.id] = site
    return found


@lru_cache
def builtin_tasks() -> dict[str, Task]:
    raw = [item for entry in _site_files() for item in entry.get("tasks", [])]
    for path in sorted((DATA / "tasks").glob("*.json")):
        raw += json.loads(path.read_text(encoding="utf-8")).get("tasks", [])
    found: dict[str, Task] = {}
    for item in raw:
        task = Task.model_validate(item)
        if task.id in found:
            raise CatalogError(f"Task {task.id} is defined twice")
        found[task.id] = task
    return found


# ---------------------------------------------------------------- custom items (studio hook)


def _studio():
    """The studio's catalog source, or None when that module does not exist yet."""
    if importlib.util.find_spec("vanguard.studio") is None:
        return None
    if importlib.util.find_spec(STUDIO_SOURCE) is None:
        return None
    return importlib.import_module(STUDIO_SOURCE)


def _custom(kind: str) -> dict:
    source = _studio()
    if source is None or not hasattr(source, kind):
        return {}
    return dict(getattr(source, kind)())


# ---------------------------------------------------------------- combined views


def personas() -> dict[str, PersonaSpec]:
    return {**_custom("personas"), **builtin_personas()}


def sites() -> dict[str, Site]:
    return {**_custom("sites"), **builtin_sites()}


def tasks() -> dict[str, Task]:
    combined = {**_custom("tasks"), **builtin_tasks()}
    known = sites()
    for task in combined.values():
        if task.site_id not in known:
            raise CatalogError(f"Task {task.id} refers to unknown site {task.site_id}")
    return combined


def persona(persona_id: str) -> PersonaSpec:
    try:
        return personas()[persona_id]
    except KeyError:
        raise CatalogError(f"Unknown persona: {persona_id}") from None


def site(site_id: str) -> Site:
    try:
        return sites()[site_id]
    except KeyError:
        raise CatalogError(f"Unknown site: {site_id}") from None


def task(task_id: str) -> Task:
    try:
        return tasks()[task_id]
    except KeyError:
        raise CatalogError(f"Unknown task: {task_id}") from None


def site_origins() -> list[str]:
    """Every catalog site's origin (built-in and custom): these may be visited."""
    return sorted({site.origin.rstrip("/") for site in sites().values()})


def docker_rewrites() -> dict[str, str]:
    """origin -> http://<docker_host> for sites that run as Compose services."""
    return {
        site.origin.rstrip("/"): f"http://{site.docker_host}"
        for site in sites().values()
        if site.docker_host
    }
