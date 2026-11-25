"""The configuration studio API: custom personas, sites and tasks (vanguard.studio).

    GET/POST          /studio/personas         list or create custom personas
    GET/PUT/DELETE    /studio/personas/{id}    one persona (GET also reads built-ins)
    ... and the same for /studio/sites and /studio/tasks (GET /studio/tasks?site_id=...).

Bodies are the contract's fields; the server sets the id (custom-<slug>-<4 hex>) and a
persona's status. Errors:
  - 422 when the data does not fit the contract or a studio rule, with the message, in
    FastAPI's usual shape ({"detail": [{"loc": [...], "msg": "..."}]});
  - 409 when the id is a built-in item's ("copy it first");
  - 404 when there is no such custom item.
A custom site's origin is allowed for runs at once: the catalog lists it (CP-G1).
"""

from collections.abc import Callable
from typing import Annotated, Any

from fastapi import APIRouter, Body, Depends, HTTPException, Response
from pydantic import ValidationError

from vanguard import catalog
from vanguard.contracts import PersonaSpec, Site, Task
from vanguard.deps import get_store
from vanguard.store import RunStore
from vanguard.studio import repository
from vanguard.studio.repository import BuiltinItem, NotFound, StudioError

router = APIRouter(prefix="/studio", tags=["studio"])


def _call(action: Callable[[], Any]) -> Any:
    """Run a repository action, turning its errors into HTTP responses."""
    try:
        return action()
    except ValidationError as error:
        detail = [
            {
                "loc": ["body", *error_item["loc"]],
                "msg": error_item["msg"],
                "type": error_item["type"],
            }
            for error_item in error.errors(include_url=False)
        ]
        raise HTTPException(422, detail) from None
    except StudioError as error:
        loc = ["body", error.field] if error.field else ["body"]
        raise HTTPException(422, [{"loc": loc, "msg": str(error), "type": "value_error"}]) from None
    except BuiltinItem as error:
        raise HTTPException(409, str(error)) from None
    except NotFound as error:
        raise HTTPException(404, str(error)) from None


def _found(item, kind: str, item_id: str):
    if item is None:
        raise HTTPException(404, f"No {kind} {item_id}")
    return item


# ---------------------------------------------------------------- personas


@router.get("/personas")
def list_personas(store: RunStore = Depends(get_store)) -> list[PersonaSpec]:
    """Custom personas only; GET /personas lists built-in and custom together."""
    return repository.list_personas(store)


@router.post("/personas", status_code=201)
def create_persona(
    data: Annotated[dict, Body()], store: RunStore = Depends(get_store)
) -> PersonaSpec:
    return _call(lambda: repository.save_persona(store, data))


@router.get("/personas/{persona_id}")
def get_persona(persona_id: str, store: RunStore = Depends(get_store)) -> PersonaSpec:
    item = repository.get_persona(store, persona_id) or catalog.builtin_personas().get(persona_id)
    return _found(item, "persona", persona_id)


@router.put("/personas/{persona_id}")
def update_persona(
    persona_id: str, data: Annotated[dict, Body()], store: RunStore = Depends(get_store)
) -> PersonaSpec:
    return _call(lambda: repository.save_persona(store, data, persona_id))


@router.delete("/personas/{persona_id}", status_code=204)
def delete_persona(persona_id: str, store: RunStore = Depends(get_store)) -> Response:
    _call(lambda: repository.delete_persona(store, persona_id))
    return Response(status_code=204)


# ---------------------------------------------------------------- sites


@router.get("/sites")
def list_sites(store: RunStore = Depends(get_store)) -> list[Site]:
    """Custom sites only; GET /sites lists built-in and custom together."""
    return repository.list_sites(store)


@router.post("/sites", status_code=201)
def create_site(data: Annotated[dict, Body()], store: RunStore = Depends(get_store)) -> Site:
    return _call(lambda: repository.save_site(store, data))


@router.get("/sites/{site_id}")
def get_site(site_id: str, store: RunStore = Depends(get_store)) -> Site:
    item = repository.get_site(store, site_id) or catalog.builtin_sites().get(site_id)
    return _found(item, "site", site_id)


@router.put("/sites/{site_id}")
def update_site(
    site_id: str, data: Annotated[dict, Body()], store: RunStore = Depends(get_store)
) -> Site:
    return _call(lambda: repository.save_site(store, data, site_id))


@router.delete("/sites/{site_id}", status_code=204)
def delete_site(site_id: str, store: RunStore = Depends(get_store)) -> Response:
    """Deletes the site and its custom tasks."""
    _call(lambda: repository.delete_site(store, site_id))
    return Response(status_code=204)


# ---------------------------------------------------------------- tasks


@router.get("/tasks")
def list_tasks(site_id: str | None = None, store: RunStore = Depends(get_store)) -> list[Task]:
    """Custom tasks, optionally on one site (built-in or custom)."""
    return repository.list_tasks(store, site_id)


@router.post("/tasks", status_code=201)
def create_task(data: Annotated[dict, Body()], store: RunStore = Depends(get_store)) -> Task:
    return _call(lambda: repository.save_task(store, data))


@router.get("/tasks/{task_id}")
def get_task(task_id: str, store: RunStore = Depends(get_store)) -> Task:
    item = repository.get_task(store, task_id) or catalog.builtin_tasks().get(task_id)
    return _found(item, "task", task_id)


@router.put("/tasks/{task_id}")
def update_task(
    task_id: str, data: Annotated[dict, Body()], store: RunStore = Depends(get_store)
) -> Task:
    return _call(lambda: repository.save_task(store, data, task_id))


@router.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: str, store: RunStore = Depends(get_store)) -> Response:
    _call(lambda: repository.delete_task(store, task_id))
    return Response(status_code=204)
