"""Limit identifiers. Definitions and detection rules live in docs/leakage-spec.md."""

from enum import StrEnum


class LimitId(StrEnum):
    NO_POINTER = "L1"  # action limit: keyboard only
    ACCESSIBILITY_TREE_ONLY = "L2"  # perception limit: ARIA snapshot only
    MAGNIFIED_VIEW = "L3"  # perception limit: magnified window only
    FIRST_TIME_KNOWLEDGE = "L4"  # knowledge limit: nothing site-specific until observed
