"""Persona specs. A persona is a bundle of limits plus how it perceives and what it knows."""

from enum import StrEnum

from pydantic import BaseModel, Field

from .actions import ToolGroup
from .limits import LimitId


class PerceptionMode(StrEnum):
    FULL = "full"  # full view (screenshot or simplified DOM, per perception alternative)
    ACCESSIBILITY_TREE = "accessibility_tree"  # ARIA snapshot only
    MAGNIFIED = "magnified"  # only what intersects the magnified window


class PersonaStatus(StrEnum):
    FULL = "full"  # limits enforced, perceived, checked and evaluated
    PREVIEW = "preview"  # limits stated in the prompt only; results not validated


class Knowledge(BaseModel):
    knows: list[str] = Field(default_factory=list, description="What this user knows up front")
    does_not_know: list[str] = Field(
        default_factory=list, description="Terms this user does not know until observed (L4)"
    )


class PersonaSpec(BaseModel):
    id: str
    name: str
    character: str = Field(description="Sprite id in the frontend, e.g. 'knock'")
    represents: str
    status: PersonaStatus
    limits: list[LimitId] = Field(default_factory=list)
    perception: PerceptionMode = PerceptionMode.FULL
    tool_groups: list[ToolGroup]
    knowledge: Knowledge = Field(default_factory=Knowledge)
    magnification: float | None = Field(None, description="Zoom factor for L3, e.g. 4.0")
    description: str = Field(description="How the persona is described to the model")
    is_control: bool = False
