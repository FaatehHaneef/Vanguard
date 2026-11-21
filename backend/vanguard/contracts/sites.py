"""Sites the agent may visit and the tasks it is given there."""

from enum import StrEnum

from pydantic import BaseModel, Field


class SiteKind(StrEnum):
    TEST = "test"  # a Vanguard test site, such as Tallowmere
    OWN = "own"  # an owner's site, verified with the snippet (A4)


class SiteSplit(StrEnum):
    TRAIN = "train"
    DEV = "dev"
    TEST = "test"


class Honeytoken(BaseModel):
    """A string planted where only a forbidden channel reveals it (spec Section 1)."""

    token: str
    rule: str = Field(description="H2b, H3b or H4c")
    limit: str = Field(description="The limit it tests: L2, L3 or L4")
    where: str = ""


class Site(BaseModel):
    id: str
    name: str
    origin: str
    kind: SiteKind = SiteKind.TEST
    split: SiteSplit = SiteSplit.DEV
    description: str = ""
    # The test manifest. Never serialised (so never sent by the API or shown to an agent).
    honeytokens: list[Honeytoken] = Field(default_factory=list, exclude=True)
    site_tokens: list[str] = Field(
        default_factory=list,
        exclude=True,
        description="Site-specific names, prices and codes a first-time visitor cannot know "
        "until they are shown (H4b)",
    )


class SuccessCheck(BaseModel):
    """Deterministic success condition, checked by code after every step."""

    url_prefix: str | None = Field(None, description="Success when the path starts with this")
    text_present: str | None = Field(None, description="Success when this text is on the page")
    answer_contains: list[str] = Field(
        default_factory=list,
        description="Success when the done() answer contains all of these (case-insensitive)",
    )


class Task(BaseModel):
    id: str
    site_id: str
    instruction: str = Field(description="What the persona is asked to do, in plain words")
    start_path: str = "/"
    success: SuccessCheck
    expected: dict[str, str] = Field(
        default_factory=dict,
        description="Expected outcome per persona id where a planted barrier applies",
    )
