"""Check a test site against the test-site kit (docs/test-site-kit.md).

    python -m vanguard.cli check-site willowbrook --dir sites/willowbrook-clinic [--live]

Static checks: the catalog entry (origin, 2 to 4 tasks with success checks, a
honeytoken for each of L2, L3 and L4, site tokens), the site folder (README.md,
MANIFEST.md, Dockerfile), every honeytoken planted in the site and listed in the
manifest, the Compose service, and no mention of Vanguard or of the test design in
anything the site could serve. With --live, the site must also answer at its origin
and at every task's start page.
"""

import re
from dataclasses import dataclass
from pathlib import Path

import httpx

from vanguard import catalog
from vanguard.settings import REPO_ROOT

# Files that describe the site for the team and are never served.
NOT_SERVED = {"README.md", "MANIFEST.md", "Dockerfile", ".dockerignore", ".gitignore"}
SKIP_DIRS = {"node_modules", "dist", "build", ".venv", "venv", "__pycache__", ".next", ".git"}
TEXT_SUFFIXES = {
    ".html", ".htm", ".css", ".js", ".mjs", ".ts", ".tsx", ".jsx", ".vue", ".svelte",
    ".py", ".jinja", ".j2", ".json", ".txt", ".md", ".astro", ".php", ".xml", ".svg",
}  # fmt: skip
# Words that would reveal the test design to an agent reading the site.
FORBIDDEN = re.compile(r"vanguard|honeytoken|leakage|planted|persona", re.IGNORECASE)
REQUIRED_LIMITS = {"L2", "L3", "L4"}


@dataclass
class Check:
    name: str
    ok: bool
    detail: str = ""


def _site_files(folder: Path) -> list[Path]:
    files = []
    for path in folder.rglob("*"):
        if any(part in SKIP_DIRS for part in path.relative_to(folder).parts):
            continue
        if path.is_file() and path.name not in NOT_SERVED and path.suffix in TEXT_SUFFIXES:
            files.append(path)
    return files


def run_checks(site_id: str, folder: Path, live: bool = False) -> list[Check]:
    checks: list[Check] = []
    try:
        site = catalog.site(site_id)
    except LookupError as error:
        return [Check("catalog entry exists", False, str(error))]
    checks.append(Check("catalog entry exists", True, site.origin))

    tasks = [task for task in catalog.tasks().values() if task.site_id == site_id]
    checks.append(Check("2 to 4 tasks", 2 <= len(tasks) <= 4, f"{len(tasks)} tasks"))
    unchecked = [
        task.id
        for task in tasks
        if not (
            task.success.url_prefix or task.success.text_present or task.success.answer_contains
        )
    ]
    checks.append(Check("every task has a success check", not unchecked, ", ".join(unchecked)))

    limits = {honeytoken.limit for honeytoken in site.honeytokens}
    checks.append(
        Check(
            "a honeytoken for each of L2, L3, L4",
            REQUIRED_LIMITS <= limits,
            f"missing {sorted(REQUIRED_LIMITS - limits)}" if not REQUIRED_LIMITS <= limits else "",
        )
    )
    checks.append(Check("site tokens listed (for H4b)", bool(site.site_tokens)))

    for name in ("README.md", "MANIFEST.md", "Dockerfile"):
        checks.append(Check(f"{name} present", (folder / name).is_file()))

    files = _site_files(folder)
    text = {path: path.read_text(encoding="utf-8", errors="ignore") for path in files}
    for honeytoken in site.honeytokens:
        planted = any(honeytoken.token in content for content in text.values())
        checks.append(Check(f"honeytoken {honeytoken.token} planted", planted))
    manifest = folder / "MANIFEST.md"
    if manifest.is_file():
        listed = manifest.read_text(encoding="utf-8")
        missing = [h.token for h in site.honeytokens if h.token not in listed]
        checks.append(Check("manifest lists every honeytoken", not missing, ", ".join(missing)))

    leaks = [
        f"{path.relative_to(folder)}: {match.group(0)}"
        for path, content in text.items()
        for match in [FORBIDDEN.search(content)]
        if match
    ]
    checks.append(
        Check(
            "nothing served mentions Vanguard or the test design", not leaks, "; ".join(leaks[:5])
        )
    )

    port = site.origin.rsplit(":", 1)[-1]
    own = folder / "compose.yml"
    compose = own.read_text(encoding="utf-8") if own.is_file() else ""
    root_compose = (REPO_ROOT / "docker-compose.yml").read_text(encoding="utf-8")
    included = (
        own.is_file()
        and own.resolve().is_relative_to(REPO_ROOT)
        and own.resolve().relative_to(REPO_ROOT).as_posix() in root_compose
    )
    checks.append(Check("compose.yml included by docker-compose.yml", bool(included)))
    checks.append(Check(f"Compose service on port {port}", f'"{port}:{port}"' in compose))
    if site.docker_host:
        service = site.docker_host.split(":", 1)[0]
        named = f"\n  {service}:\n" in compose
        checks.append(Check(f"Compose service named {service}", named))
    else:
        checks.append(Check("docker_host set in the catalog file", False))

    if live:
        for path in sorted({"/", *(task.start_path for task in tasks)}):
            try:
                status = httpx.get(site.origin + path, timeout=10).status_code
            except httpx.HTTPError as error:
                status = type(error).__name__
            checks.append(Check(f"answers at {path}", status == 200, str(status)))
    return checks


def report(checks: list[Check]) -> str:
    lines = [f"{'PASS' if c.ok else 'FAIL'}  {c.name}{f'  ({c.detail})' if c.detail else ''}"
             for c in checks]  # fmt: skip
    failed = sum(not c.ok for c in checks)
    lines.append(f"\n{len(checks) - failed} of {len(checks)} checks passed")
    return "\n".join(lines)
