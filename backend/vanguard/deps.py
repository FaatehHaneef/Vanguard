"""Shared FastAPI dependencies, so route modules in vanguard.routes need not import api."""

from vanguard.settings import Settings, get_settings
from vanguard.store import RunStore

_store: RunStore | None = None


def open_store(settings: Settings | None = None) -> RunStore:
    """Open the run store (called once, when the API starts)."""
    global _store
    _store = RunStore((settings or get_settings()).database_url)
    _store.create_schema()
    return _store


def get_store() -> RunStore:
    if _store is None:
        raise RuntimeError("store not initialised")
    return _store


__all__ = ["get_settings", "get_store", "open_store"]
