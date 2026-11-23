"""API route modules, included by vanguard.api automatically.

Each module in this package exposes `router` (a fastapi.APIRouter). Adding a feature's
endpoints means adding one file here, for example routes/studio.py with
`router = APIRouter(prefix="/studio", tags=["studio"])`; api.py never needs editing, so
parallel work does not conflict. Use vanguard.deps for the store and the settings.
"""

import importlib
import pkgutil

from fastapi import APIRouter


def routers() -> list[tuple[str, APIRouter]]:
    """(module name, router) for every module here that exposes one, sorted by name."""
    found = []
    for info in sorted(pkgutil.iter_modules(__path__), key=lambda m: m.name):
        if info.name.startswith("_"):
            continue
        module = importlib.import_module(f"{__name__}.{info.name}")
        router = getattr(module, "router", None)
        if isinstance(router, APIRouter):
            found.append((info.name, router))
    return found
