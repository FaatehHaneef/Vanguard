"""The executor interface: the agent's hands and eyes on a real (or fake) browser.

The real implementation drives Chromium with Playwright from outside the page, so key
presses and clicks are genuine input events and their modality is known exactly. A
fake implementation (fake.py) simulates a tiny site for tests.
"""

from dataclasses import dataclass, field
from typing import Protocol

from vanguard.contracts import Action, BrowserEvent, Observation, PersonaSpec, Rect, Site, Task


@dataclass
class ExecutionResult:
    events: list[BrowserEvent] = field(default_factory=list)
    url_after: str | None = None
    focus_after: str | None = None
    target_box: Rect | None = None
    error: str | None = None


class Executor(Protocol):
    async def start(self, site: Site, task: Task, persona: PersonaSpec) -> None:
        """Open a fresh browser context at the task's start page."""

    async def observe(self) -> Observation:
        """What this persona perceives right now (perception mode set by the persona)."""

    async def execute(self, action: Action) -> ExecutionResult:
        """Perform one allowed action and report what happened in the page."""

    async def current_url(self) -> str: ...

    async def page_text(self) -> str:
        """Visible text of the page, for deterministic success checks."""

    async def close(self) -> None: ...
