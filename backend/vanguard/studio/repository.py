"""Reading and writing custom personas, sites and tasks.

Every function takes the RunStore and uses its session. Writes take the item as plain
data (what the studio form sends), fill in what the server decides (the id, a persona's
status), check the studio's rules and validate the result against the contract before
saving. Built-in items are never written: they live in the catalog's JSON files.

Errors:
  - BuiltinItem: the id belongs to a built-in item (read-only; copy it first);
  - NotFound: no custom item with that id;
  - StudioError: the data breaks a studio rule (pydantic's ValidationError is raised
    as is when the data does not fit the contract).
"""

from collections.abc import Callable
from typing import Any
from urllib.parse import urlsplit

from sqlalchemy import select

from vanguard import catalog
from vanguard.contracts import PersonaSpec, PersonaStatus, Site, SiteKind, Task
from vanguard.store import RunStore

from .models import (
    CustomPersonaRow,
    CustomSiteRow,
    CustomTaskRow,
    _CustomItem,
    ensure_tables,
    new_id,
)


class StudioError(ValueError):
    """A studio rule is broken. `field` names the offending field, when there is one."""

    def __init__(self, message: str, field: str | None = None):
        super().__init__(message)
        self.field = field


class BuiltinItem(Exception):
    pass


class NotFound(LookupError):
    pass


# ---------------------------------------------------------------- shared helpers


def _session(store: RunStore):
    ensure_tables(store.engine)
    return store._session()


def _list(store: RunStore, row_type: type[_CustomItem]) -> list:
    query = select(row_type).order_by(row_type.created_at, row_type.id)
    with _session(store) as session:
        items = []
        for row in session.scalars(query):
            try:
                items.append(row.item())
            except ValueError:  # a row that no longer fits the contract is skipped
                continue
        return items


def _get(store: RunStore, row_type: type[_CustomItem], item_id: str):
    with _session(store) as session:
        row = session.get(row_type, item_id)
        return row.item() if row else None


def _ids(store: RunStore, row_type: type[_CustomItem]) -> set[str]:
    with _session(store) as session:
        return set(session.scalars(select(row_type.id)))


def _check_not_builtin(kind: str, item_id: str | None, builtins: dict) -> None:
    if item_id is not None and item_id in builtins:
        raise BuiltinItem(f"The built-in {kind} {item_id} is read-only: copy it first.")


def _save(
    store: RunStore,
    row_type: type[_CustomItem],
    kind: str,
    builtins: dict,
    item_id: str | None,
    id_source: str,
    build: Callable[[str], Any],
):
    """Create (item_id None) or replace a custom item. `build(id)` returns the validated
    contract item for that id."""
    _check_not_builtin(kind, item_id, builtins)
    creating = item_id is None
    if creating:
        item_id = new_id(id_source, set(builtins) | _ids(store, row_type))
    elif _get(store, row_type, item_id) is None:
        raise NotFound(f"No custom {kind} {item_id}")
    # Validate first, so a rejected item never opens a write.
    item = build(item_id)
    with _session(store) as session, session.begin():
        row = session.get(row_type, item_id)
        if row is None:
            if not creating:
                raise NotFound(f"No custom {kind} {item_id}")
            row = row_type(id=item_id)
            session.add(row)
        row.set_data(item)
    return item


def _delete(store: RunStore, row_type: type[_CustomItem], kind: str, builtins: dict, item_id: str):
    _check_not_builtin(kind, item_id, builtins)
    with _session(store) as session, session.begin():
        row = session.get(row_type, item_id)
        if row is None:
            raise NotFound(f"No custom {kind} {item_id}")
        session.delete(row)


def _text(data: dict, field: str, label: str) -> str:
    value = data.get(field)
    if not isinstance(value, str) or not value.strip():
        raise StudioError(f"{label} is required.", field)
    return value.strip()


# ---------------------------------------------------------------- personas


def persona_status(spec: PersonaSpec) -> PersonaStatus:
    """`full` only when the persona applies its limits exactly as a validated built-in
    bundle does (docs/leakage-spec.md, Section 4): the same limits, perception, tool
    groups and magnification as a built-in persona whose status is full. Anything else
    states its limits in the prompt only, so it is a preview."""
    for builtin in catalog.builtin_personas().values():
        if (
            builtin.status is PersonaStatus.FULL
            and set(builtin.limits) == set(spec.limits)
            and builtin.perception == spec.perception
            and set(builtin.tool_groups) == set(spec.tool_groups)
            and builtin.magnification == spec.magnification
        ):
            return PersonaStatus.FULL
    return PersonaStatus.PREVIEW


def characters() -> set[str]:
    return {persona.character for persona in catalog.builtin_personas().values()}


def _persona(data: dict, persona_id: str) -> PersonaSpec:
    name = _text(data, "name", "A name")
    _text(data, "description", "A description")
    character = data.get("character")
    if character not in characters():
        raise StudioError(
            f"Choose one of the characters: {', '.join(sorted(characters()))}.", "character"
        )
    if not data.get("tool_groups"):
        raise StudioError(
            "Choose at least one group of actions the persona may use.", "tool_groups"
        )
    fields = {**data, "id": persona_id, "name": name, "status": "preview", "is_control": False}
    if fields.get("perception") == "magnified":
        try:
            magnification = float(fields.get("magnification") or 0)
        except (TypeError, ValueError):
            magnification = 0
        if magnification <= 1:
            raise StudioError(
                "A magnified view needs a magnification above 1, for example 4.", "magnification"
            )
    else:
        fields["magnification"] = None
    spec = PersonaSpec.model_validate(fields)
    return spec.model_copy(update={"status": persona_status(spec)})


def list_personas(store: RunStore) -> list[PersonaSpec]:
    return _list(store, CustomPersonaRow)


def get_persona(store: RunStore, persona_id: str) -> PersonaSpec | None:
    return _get(store, CustomPersonaRow, persona_id)


def save_persona(store: RunStore, data: dict, persona_id: str | None = None) -> PersonaSpec:
    return _save(
        store,
        CustomPersonaRow,
        "persona",
        catalog.builtin_personas(),
        persona_id,
        str(data.get("name") or "persona"),
        lambda new: _persona(data, new),
    )


def delete_persona(store: RunStore, persona_id: str) -> None:
    _delete(store, CustomPersonaRow, "persona", catalog.builtin_personas(), persona_id)


# ---------------------------------------------------------------- sites


def normalise_origin(value: Any) -> str:
    """`https://shop.example.com` from a site address; StudioError unless it is an
    http(s) origin with a host and no path, query or fragment."""
    text = value.strip() if isinstance(value, str) else ""
    parts = urlsplit(text)
    if parts.scheme not in ("http", "https") or not parts.hostname:
        raise StudioError(
            "The address must start with http:// or https:// and name a host, "
            "for example https://shop.example.com.",
            "origin",
        )
    if parts.path not in ("", "/") or parts.query or parts.fragment:
        raise StudioError(
            "Give only the site's address, for example https://shop.example.com, without a "
            "page path. Tasks give their own start page.",
            "origin",
        )
    return f"{parts.scheme}://{parts.netloc.lower()}"


def _site(data: dict, site_id: str) -> Site:
    name = _text(data, "name", "A name")
    fields = {
        "id": site_id,
        "name": name,
        "origin": normalise_origin(data.get("origin")),
        "kind": data.get("kind") or SiteKind.OWN,
        "description": (data.get("description") or "").strip(),
    }
    if "split" in data and data["split"]:
        fields["split"] = data["split"]
    return Site.model_validate(fields)


def list_sites(store: RunStore) -> list[Site]:
    return _list(store, CustomSiteRow)


def get_site(store: RunStore, site_id: str) -> Site | None:
    return _get(store, CustomSiteRow, site_id)


def save_site(store: RunStore, data: dict, site_id: str | None = None) -> Site:
    return _save(
        store,
        CustomSiteRow,
        "site",
        catalog.builtin_sites(),
        site_id,
        str(data.get("name") or "site"),
        lambda new: _site(data, new),
    )


def delete_site(store: RunStore, site_id: str) -> None:
    """Delete a custom site and every custom task on it."""
    _check_not_builtin("site", site_id, catalog.builtin_sites())
    with _session(store) as session, session.begin():
        row = session.get(CustomSiteRow, site_id)
        if row is None:
            raise NotFound(f"No custom site {site_id}")
        for task_row in session.scalars(select(CustomTaskRow)):
            if task_row.data.get("site_id") == site_id:
                session.delete(task_row)
        session.delete(row)


# ---------------------------------------------------------------- tasks


def _task(store: RunStore, data: dict, task_id: str) -> Task:
    instruction = _text(data, "instruction", "An instruction")
    site_id = data.get("site_id")
    known = {**catalog.builtin_sites(), **{s.id: s for s in list_sites(store)}}
    if site_id not in known:
        raise StudioError(f"There is no site {site_id!r}. Choose an existing site.", "site_id")
    start_path = (data.get("start_path") or "/").strip()
    if not start_path.startswith("/"):
        raise StudioError(
            "The start page must be a path on the site, starting with /.", "start_path"
        )
    success = dict(data.get("success") or {})
    success["answer_contains"] = [
        item.strip() for item in success.get("answer_contains") or [] if str(item).strip()
    ]
    for key in ("url_prefix", "text_present"):
        if isinstance(success.get(key), str):
            success[key] = success[key].strip() or None
    if not (success.get("url_prefix") or success.get("text_present") or success["answer_contains"]):
        raise StudioError(
            "Give the task a success check: a page address it reaches, text that appears on "
            "the page, or words the final answer must contain.",
            "success",
        )
    if success.get("url_prefix") and not success["url_prefix"].startswith("/"):
        raise StudioError("A success address must be a path starting with /.", "success")
    return Task.model_validate(
        {
            "id": task_id,
            "site_id": site_id,
            "instruction": instruction,
            "scenario": data.get("scenario") or None,
            "start_path": start_path,
            "success": success,
            "expected": data.get("expected") or {},
        }
    )


def list_tasks(store: RunStore, site_id: str | None = None) -> list[Task]:
    tasks = _list(store, CustomTaskRow)
    return [task for task in tasks if site_id is None or task.site_id == site_id]


def get_task(store: RunStore, task_id: str) -> Task | None:
    return _get(store, CustomTaskRow, task_id)


def save_task(store: RunStore, data: dict, task_id: str | None = None) -> Task:
    return _save(
        store,
        CustomTaskRow,
        "task",
        catalog.builtin_tasks(),
        task_id,
        str(data.get("instruction") or "task"),
        lambda new: _task(store, data, new),
    )


def delete_task(store: RunStore, task_id: str) -> None:
    _delete(store, CustomTaskRow, "task", catalog.builtin_tasks(), task_id)
