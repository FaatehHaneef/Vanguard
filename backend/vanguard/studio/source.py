"""The catalog hook: custom items for vanguard.catalog (see its module docstring).

vanguard.catalog calls personas(), sites() and tasks() on every lookup. Each reads the
saved custom items afresh (no caching), so an edit in the studio appears at once in the
lobby, the site picker, runs, the checker and the results.

Custom items live in the API's database, opened by vanguard.deps when the API starts;
runs execute in the API process, so they see them too. Where no API store is open (the
command line, or tests that do not start the API) there are no custom items, and the
catalog holds the built-in items only. A database error never breaks the catalog: the
custom items are then left out.
"""

import logging

from sqlalchemy.exc import SQLAlchemyError

from vanguard import deps
from vanguard.contracts import PersonaSpec, Site, Task
from vanguard.store import RunStore

from . import repository

log = logging.getLogger(__name__)


def _store() -> RunStore | None:
    try:
        return deps.get_store()
    except RuntimeError:  # the API has not opened its store
        return None


def _by_id(read) -> dict:
    store = _store()
    if store is None:
        return {}
    try:
        return {item.id: item for item in read(store)}
    except SQLAlchemyError:
        log.exception("custom studio items could not be read")
        return {}


def personas() -> dict[str, PersonaSpec]:
    return _by_id(repository.list_personas)


def sites() -> dict[str, Site]:
    return _by_id(repository.list_sites)


def tasks() -> dict[str, Task]:
    return _by_id(repository.list_tasks)
