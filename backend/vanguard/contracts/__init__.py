"""Shared data contracts. Every module and the frontend agree on these shapes.

Changing a contract is a team decision: update docs/leakage-spec.md first if the
change affects leakage, then bump CONTRACT_VERSION.
"""

from .actions import TOOL_GROUPS, Action, Tool, ToolGroup
from .batches import BatchGroup, BatchRequest, BatchStatus
from .limits import LimitId
from .persona import Knowledge, PerceptionMode, PersonaSpec, PersonaStatus
from .runs import Condition, EnforcementOption, RunConfig, RunOutcome, RunStatus, RunSummary
from .sites import Site, SiteKind, SiteSplit, SuccessCheck, Task
from .steps import BrowserEvent, GateDecision, Observation, Rect, StepRecord

CONTRACT_VERSION = "0.2.0"

__all__ = [
    "CONTRACT_VERSION",
    "TOOL_GROUPS",
    "Action",
    "BatchGroup",
    "BatchRequest",
    "BatchStatus",
    "BrowserEvent",
    "Condition",
    "EnforcementOption",
    "GateDecision",
    "Knowledge",
    "LimitId",
    "Observation",
    "PerceptionMode",
    "PersonaSpec",
    "PersonaStatus",
    "Rect",
    "RunConfig",
    "RunOutcome",
    "RunStatus",
    "RunSummary",
    "Site",
    "SiteKind",
    "SiteSplit",
    "StepRecord",
    "SuccessCheck",
    "Task",
    "Tool",
    "ToolGroup",
]
