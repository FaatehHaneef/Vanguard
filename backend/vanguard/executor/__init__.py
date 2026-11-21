"""Executors. The Playwright executor (playwright.py) is added with the worker."""

from .base import ExecutionResult, Executor
from .fake import FakeExecutor, FakePage

__all__ = ["ExecutionResult", "Executor", "FakeExecutor", "FakePage"]
