"""Where the browser may go, and how it reaches each site.

Allowed origins are every catalog site's origin (built-in and custom) plus any extra ones
in the settings. Inside Docker, requests to a catalog site go to its Compose service
(Site.docker_host) while the page keeps its usual address.
"""

from vanguard import catalog
from vanguard.settings import Settings


def allowed_origins(settings: Settings) -> list[str]:
    extra = [origin.rstrip("/") for origin in settings.allowed_origins]
    return sorted({*catalog.site_origins(), *extra})


def rewrites(settings: Settings) -> dict[str, str]:
    found = catalog.docker_rewrites() if settings.in_docker else {}
    return {**found, **settings.origin_rewrites}
