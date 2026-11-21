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


class Site(BaseModel):
    id: str
    name: str
    origin: str
    kind: SiteKind = SiteKind.TEST
    split: SiteSplit = SiteSplit.DEV
    description: str = ""


class SuccessCheck(BaseModel):
    """Deterministic success condition, checked by code after every step."""

    url_prefix: str | None = Field(None, description="Success when the path starts with this")
    text_present: str | None = Field(None, description="Success when this text is on the page")


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
