"""Storage for custom personas, sites and tasks.

Each table holds one item per row: `data` is the item exactly as its contract model
serialises it (PersonaSpec, Site, Task), so reading a row back is a single
`model_validate`. Every write validates `data` against the contract before saving.
"""

import re
import secrets
from datetime import UTC, datetime
from typing import ClassVar

from pydantic import BaseModel
from sqlalchemy import JSON, DateTime, Engine, String
from sqlalchemy.orm import Mapped, mapped_column

from vanguard.contracts import PersonaSpec, Site, Task
from vanguard.store import Base


def _now() -> datetime:
    return datetime.now(UTC)


class _CustomItem:
    id: Mapped[str] = mapped_column(String(80), primary_key=True)
    data: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    contract: ClassVar[type[BaseModel]]

    def set_data(self, item: BaseModel) -> None:
        """Validate the item against the row's contract, then store it."""
        validated = self.contract.model_validate(item.model_dump(mode="json"))
        if validated.id != self.id:
            raise ValueError(f"item id {validated.id} does not match row id {self.id}")
        # Fields marked exclude=True (a site's test manifest) are never stored.
        self.data = validated.model_dump(mode="json")
        self.updated_at = _now()

    def item(self) -> BaseModel:
        return self.contract.model_validate(self.data)


class CustomPersonaRow(_CustomItem, Base):
    __tablename__ = "custom_personas"
    contract = PersonaSpec


class CustomSiteRow(_CustomItem, Base):
    __tablename__ = "custom_sites"
    contract = Site


class CustomTaskRow(_CustomItem, Base):
    __tablename__ = "custom_tasks"
    contract = Task


TABLES = [CustomPersonaRow.__table__, CustomSiteRow.__table__, CustomTaskRow.__table__]
_ready: set[int] = set()


def ensure_tables(engine: Engine) -> None:
    """Create the studio tables on this engine if they are missing (once per engine)."""
    if id(engine) in _ready:
        return
    Base.metadata.create_all(engine, tables=TABLES)
    _ready.add(id(engine))


def slugify(text: str, words: int = 6) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    slug = "-".join(slug.split("-")[:words])[:40].strip("-")
    return slug or "item"


def new_id(text: str, taken: set[str]) -> str:
    """`custom-<slug>-<4 hex>`, never one of `taken` (built-in and existing ids)."""
    while True:
        candidate = f"custom-{slugify(text)}-{secrets.token_hex(2)}"
        if candidate not in taken:
            return candidate
