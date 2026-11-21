"""Built-in personas, sites and tasks, loaded from the JSON files in ./data.

The files are the source of truth so that non-programmers can read and review them.
Every file is validated against the contracts when it is loaded.
"""

import json
from functools import lru_cache
from pathlib import Path

from vanguard.contracts import PersonaSpec, Site, Task

DATA = Path(__file__).parent / "data"


class CatalogError(LookupError):
    pass


@lru_cache
def personas() -> dict[str, PersonaSpec]:
    specs = [
        PersonaSpec.model_validate_json(path.read_text(encoding="utf-8"))
        for path in sorted((DATA / "personas").glob("*.json"))
    ]
    return {spec.id: spec for spec in specs}


@lru_cache
def _sites_file() -> dict:
    return json.loads((DATA / "sites.json").read_text(encoding="utf-8"))


@lru_cache
def sites() -> dict[str, Site]:
    return {site.id: site for site in map(Site.model_validate, _sites_file()["sites"])}


@lru_cache
def tasks() -> dict[str, Task]:
    loaded = [Task.model_validate(item) for item in _sites_file()["tasks"]]
    known = sites()
    for task in loaded:
        if task.site_id not in known:
            raise CatalogError(f"Task {task.id} refers to unknown site {task.site_id}")
    return {task.id: task for task in loaded}


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
