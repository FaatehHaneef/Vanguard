"""Deterministic task success and stuck detection. No model is involved."""

from urllib.parse import urlsplit

from vanguard.contracts import Action, StepRecord, Task, Tool


def page_success(task: Task, url: str, page_text: str) -> bool:
    check = task.success
    if check.url_prefix and urlsplit(url).path.startswith(check.url_prefix):
        return True
    if check.text_present and check.text_present.lower() in page_text.lower():
        return True
    return False


def answer_success(task: Task, action: Action) -> bool:
    """A done() answer succeeds only if the task defines answer checks and all of them match."""
    if action.tool is not Tool.DONE or not task.success.answer_contains:
        return False
    answer = (action.answer or "").lower()
    return all(part.lower() in answer for part in task.success.answer_contains)


def is_stuck(history: list[StepRecord], window: int) -> bool:
    """Stuck: the last `window` steps changed neither the URL nor the focus nor the view."""
    if len(history) < window:
        return False
    recent = history[-window:]
    states = {(step.url_after, step.focus_after, step.observation.content) for step in recent}
    return len(states) == 1
