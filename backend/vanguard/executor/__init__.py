"""Executors. playwright.py drives a real browser (import it directly; it needs the
worker extra). fake.py simulates a tiny site for tests."""

from .base import ExecutionResult, Executor
from .fake import FakeExecutor, FakePage

__all__ = ["ExecutionResult", "Executor", "FakeExecutor", "FakePage"]
