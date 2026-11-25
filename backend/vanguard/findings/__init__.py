"""Audit findings and failure attribution, computed by code from the stored runs.

Usability findings (instructor's point 7), per run:
  - inaccessible control: a control the persona tried to use with a means its limits
    rule out (refused by the gate or the verifier, or flagged by the checker) and did not
    reach within them before the run ended. This is a candidate, not proof: the control
    may be reachable by a route the persona did not find in time;
  - navigation failure: actions that failed in the page, refused routes, a stuck run;
  - repeated actions: the same action again while nothing changed, or again right after
    it was refused;
  - confusing workflow: far more steps than the control agent needed for the same task,
    or coming back to the same page again and again;
  - failed task: the task was not completed (with the cause from vanguard.failures).

Attribution of every failed run (point 9), using the control (unrestricted) runs of the
same task and the site manifest's expected outcome (Task.expected):
  - infrastructure: the model or the browser failed, so nothing can be concluded;
  - site: the control mostly fails too, so the interface or the task is the problem;
  - restriction: the control mostly succeeds and this persona ran into its own limits
    (refused actions, checker flags, or a barrier the manifest plants for this persona);
  - agent: the control mostly succeeds and no limit explains the failure;
  - unknown: no control run to compare with and nothing in the manifest.

Every report carries the limits statement (point 17). Nothing here asks a model.
"""

from collections import Counter, defaultdict
from statistics import median

from vanguard import catalog, failures, results
from vanguard.checker import RunLeakage
from vanguard.contracts import EnforcementOption, RunOutcome, RunStatus, RunSummary, StepRecord
from vanguard.contracts.findings import (
    LIMITS_STATEMENT,
    Attribution,
    Finding,
    FindingKind,
    FindingsReport,
    RunAttribution,
)
from vanguard.metrics import repeated_attempts
from vanguard.settings import Settings
from vanguard.store import RunStore

NOT_LIMIT_RULES = {None, "S0", "invalid"}  # safety and unusable output are not limits
INFRASTRUCTURE_CAUSES = {"model_unavailable", "executor_error"}
LONG_FACTOR = 2.0  # "far longer": more than twice the control's median steps
LONG_MIN_STEPS = 6
REVISITS = 3  # coming back to the same page this many separate times
CONTROL_FAILS = 0.5  # the control "mostly fails" below this success rate
# Refused or flagged steps make the limits the explanation from this share of a run up;
# a single refusal that the persona worked around is not the reason a run failed.
LIMIT_SHARE = 0.25


# ---------------------------------------------------------------- per-step helpers


def element_label(step: StepRecord, ref: str) -> str:
    """The control as the persona perceived it: its line in the observation."""
    for line in step.observation.content.splitlines():
        if line.startswith(f"[{ref}]"):
            return line[len(ref) + 2 :].strip()[:120] or ref
    return ref


def _limit_refusal(step: StepRecord) -> bool:
    return (
        step.proposed is not None
        and not step.gate.allowed
        and step.gate.rule not in (NOT_LIMIT_RULES)
    )


def _path(url: str | None) -> str:
    if not url:
        return ""
    rest = url.split("://", 1)[-1]
    return "/" + rest.split("/", 1)[1].split("#")[0] if "/" in rest else "/"


# ---------------------------------------------------------------- findings for one run


def reached_later(steps: list[StepRecord], after: int, path: str, ref: str) -> bool:
    """Whether the persona later reached this control within its limits: on the same
    page, the focus landed on it or an allowed action used it."""
    for step in steps:
        if step.index <= after or _path(step.observation.url) != path:
            continue
        used = (
            step.proposed is not None
            and step.gate.allowed
            and step.executed
            and ref in (step.proposed.ref, step.proposed.to_ref)
        )
        if used or step.focus_after == ref:
            return True
    return False


def inaccessible_controls(steps: list[StepRecord], leakage: RunLeakage) -> list[Finding]:
    """Controls the persona tried to use outside its limits and never reached within
    them afterwards. A refused click on a link that the persona then reached with Tab
    is not a finding: the control works for this persona."""
    flagged = {verdict.index for verdict in leakage.steps if verdict.attempted}
    grouped: dict[tuple[str, str], list[int]] = defaultdict(list)
    for step in steps:
        action = step.proposed
        if action is None or not (action.ref or action.to_ref):
            continue
        if not (_limit_refusal(step) or step.index in flagged):
            continue
        path = _path(step.observation.url)
        for ref in (action.ref, action.to_ref):
            if ref and not reached_later(steps, step.index, path, ref):
                grouped[(path, element_label(step, ref))].append(step.index)
    return [
        Finding(
            kind=FindingKind.INACCESSIBLE_CONTROL,
            run_id=steps[0].run_id,
            steps=indexes,
            element=label,
            url=path,
            summary=f"Tried to use {label!r} on {path} with a means outside the persona's "
            f"limits ({len(indexes)} time{'s' if len(indexes) > 1 else ''}) and did not reach "
            "it within them before the run ended. A person should check whether it can be "
            "reached at all",
        )
        for (path, label), indexes in grouped.items()
    ]


def navigation_failures(summary: RunSummary, steps: list[StepRecord]) -> list[Finding]:
    out = []
    errors = [s for s in steps if s.execution_error]
    if errors:
        first = errors[0].execution_error or ""
        out.append(
            Finding(
                kind=FindingKind.NAVIGATION_FAILURE,
                run_id=summary.id,
                steps=[s.index for s in errors],
                url=_path(errors[0].observation.url),
                summary=f"{len(errors)} action(s) failed in the page, first: {first[:160]}",
            )
        )
    routes = [
        s
        for s in steps
        if s.proposed is not None and s.proposed.tool == "goto" and not s.gate.allowed
    ]
    if routes:
        out.append(
            Finding(
                kind=FindingKind.NAVIGATION_FAILURE,
                run_id=summary.id,
                steps=[s.index for s in routes],
                summary=f"{len(routes)} direct address(es) refused: "
                + ", ".join(sorted({s.gate.rule or "?" for s in routes})),
            )
        )
    if summary.outcome is RunOutcome.STUCK and steps:
        out.append(
            Finding(
                kind=FindingKind.NAVIGATION_FAILURE,
                run_id=summary.id,
                steps=[steps[-1].index],
                url=_path(steps[-1].observation.url),
                summary=f"Stuck on {_path(steps[-1].observation.url)}: nothing changed for "
                "several steps",
            )
        )
    return out


def repeated_steps(steps: list[StepRecord]) -> list[int]:
    """The steps that vanguard.metrics.repeated_attempts counts (one definition for the
    metric and the finding): a step is a repeat when the count rises at it."""
    ordered = sorted(steps, key=lambda step: step.index)
    out, before = [], 0
    for position in range(1, len(ordered)):
        now = repeated_attempts(ordered[: position + 1])
        if now > before:
            out.append(ordered[position].index)
        before = now
    return out


def repeated_actions(summary: RunSummary, steps: list[StepRecord]) -> list[Finding]:
    repeats = repeated_steps(steps)
    if not repeats:
        return []
    return [
        Finding(
            kind=FindingKind.REPEATED_ACTIONS,
            run_id=summary.id,
            steps=repeats,
            summary=f"{len(repeats)} step(s) repeated the previous action without effect",
        )
    ]


def confusing_workflow(
    summary: RunSummary, steps: list[StepRecord], control_steps: list[int]
) -> list[Finding]:
    out = []
    if control_steps and len(steps) >= LONG_MIN_STEPS:
        typical = median(control_steps)
        if len(steps) > LONG_FACTOR * typical:
            out.append(
                Finding(
                    kind=FindingKind.CONFUSING_WORKFLOW,
                    run_id=summary.id,
                    summary=f"{len(steps)} steps where the control needed about {typical:g}",
                )
            )
    visits: Counter = Counter()
    last = None
    for step in steps:
        path = _path(step.observation.url)
        if path != last:
            visits[path] += 1
            last = path
    for path, count in visits.items():
        if count >= REVISITS:
            out.append(
                Finding(
                    kind=FindingKind.CONFUSING_WORKFLOW,
                    run_id=summary.id,
                    url=path,
                    summary=f"Came back to {path} {count} times",
                )
            )
    return out


def failed_task(summary: RunSummary, failure: failures.RunFailure) -> list[Finding]:
    if summary.outcome is RunOutcome.SUCCESS:
        return []
    cause = failure.primary
    meaning = failures.CAUSES.get(cause, "") if cause else ""
    return [
        Finding(
            kind=FindingKind.FAILED_TASK,
            run_id=summary.id,
            summary=f"Task not completed ({summary.outcome.value if summary.outcome else '?'})"
            + (f": {meaning}" if meaning else ""),
        )
    ]


# ---------------------------------------------------------------- attribution


def attribute(
    summary: RunSummary,
    steps: list[StepRecord],
    leakage: RunLeakage,
    failure: failures.RunFailure,
    controls: list[RunSummary],
    twins: list[RunSummary] | None = None,
) -> RunAttribution:
    """Why a run failed. `twins` are finished runs of the same persona and task with its
    limits only described (prompt-only): if those mostly succeed, the enforced limit is
    what made this run fail (instructor's point 6 used for point 9)."""
    persona = catalog.persona(summary.config.persona_id)
    task = catalog.task(summary.config.task_id)
    expected = task.expected.get(persona.id)
    others = [run for run in controls if run.id != summary.id]
    rate = (
        sum(run.outcome is RunOutcome.SUCCESS for run in others) / len(others) if others else None
    )
    base = dict(
        run_id=summary.id,
        label=summary.config.label(),
        outcome=summary.outcome.value if summary.outcome else None,
        control_runs=len(others),
        control_success_rate=rate,
        expected=expected,
    )

    if failure.primary in INFRASTRUCTURE_CAUSES:
        reason = failures.CAUSES[failure.primary]
        return RunAttribution(**base, attribution=Attribution.INFRASTRUCTURE, reason=reason)

    refusals = sum(_limit_refusal(step) for step in steps)
    flagged = 0 if persona.is_control else leakage.attempted_steps
    blocked = inaccessible_controls(steps, leakage) if steps else []
    planted = bool(expected) and expected.split(":", 1)[0].strip() in ("blocked", "workaround")
    share = (refusals + flagged) / len(steps) if steps else 0.0
    limit_evidence = []
    if blocked:
        names = ", ".join(sorted({item.element or "?" for item in blocked}))[:200]
        limit_evidence.append(f"it did not reach {names} within its limits before the run ended")
    if share >= LIMIT_SHARE:
        limit_evidence.append(f"{refusals} refused and {flagged} flagged of {len(steps)} steps")
    if planted:
        limit_evidence.append(f"the site plants a barrier for it ({expected})")

    if rate is not None and rate < CONTROL_FAILS:
        return RunAttribution(
            **base,
            attribution=Attribution.SITE,
            reason=f"The control agent also fails this task ({rate:.0%} of {len(others)} "
            "control runs succeed)",
        )
    if persona.is_control:
        if rate is None:
            return RunAttribution(
                **base, attribution=Attribution.UNKNOWN, reason="No other control run to compare"
            )
        return RunAttribution(
            **base,
            attribution=Attribution.AGENT,
            reason=f"Other control runs mostly succeed ({rate:.0%}); this one did not",
        )
    enforced = set(summary.config.enforcement) - {EnforcementOption.PROMPT_ONLY}
    twin_runs = [run for run in (twins or []) if run.id != summary.id]
    if enforced and twin_runs and not persona.is_control:
        twin_rate = sum(run.outcome is RunOutcome.SUCCESS for run in twin_runs) / len(twin_runs)
        if twin_rate >= CONTROL_FAILS:
            methods = "+".join(sorted(option.value for option in enforced))
            return RunAttribution(
                **base,
                attribution=Attribution.RESTRICTION,
                reason=f"The same persona succeeds on this task when its limits are only "
                f"described ({twin_rate:.0%} of {len(twin_runs)} runs); with them enforced "
                f"({methods}) it failed",
            )
    if limit_evidence and (rate is not None or planted):
        context = (
            f"The control agent succeeds ({rate:.0%} of {len(others)} runs)"
            if rate is not None
            else "No control run to compare"
        )
        return RunAttribution(
            **base,
            attribution=Attribution.RESTRICTION,
            reason=f"{context}; this persona ran into its limits: " + "; ".join(limit_evidence),
        )
    if rate is None:
        return RunAttribution(
            **base,
            attribution=Attribution.UNKNOWN,
            reason="No control run of this task to compare with",
        )
    cause = failures.CAUSES.get(failure.primary or "", "it did not finish")
    return RunAttribution(
        **base,
        attribution=Attribution.AGENT,
        reason=f"The control agent succeeds ({rate:.0%} of {len(others)} runs) and no limit "
        f"explains the failure: {cause[:1].lower() + cause[1:]}",
    )


# ---------------------------------------------------------------- reports


def _control_runs(
    store: RunStore, summary: RunSummary, cache: dict
) -> tuple[list[RunSummary], list[int]]:
    """Finished control runs of the same task: from the same batch when it has any,
    otherwise from every batch. Returns the runs and the step counts of the successes."""
    key = (summary.config.task_id, summary.config.batch_id)
    if key not in cache:
        everything = cache.setdefault("_all", store.list_runs(limit=100_000))
        controls = [
            run
            for run in everything
            if run.status is RunStatus.FINISHED
            and run.config.task_id == summary.config.task_id
            and catalog.persona(run.config.persona_id).is_control
        ]
        same_batch = [run for run in controls if run.config.batch_id == summary.config.batch_id]
        chosen = same_batch or controls
        steps = [run.steps for run in chosen if run.outcome is RunOutcome.SUCCESS]
        cache[key] = (chosen, steps)
    return cache[key]


def _twin_runs(cache: dict, summary: RunSummary) -> list[RunSummary]:
    """Finished prompt-only runs of the same persona and task (any batch)."""
    return [
        run
        for run in cache["_all"]
        if run.status is RunStatus.FINISHED
        and run.config.persona_id == summary.config.persona_id
        and run.config.task_id == summary.config.task_id
        and run.config.enforcement == [EnforcementOption.PROMPT_ONLY]
    ]


def report_for(
    store: RunStore, summaries: list[RunSummary], settings: Settings, scope: str
) -> FindingsReport:
    found: list[Finding] = []
    attributions: list[RunAttribution] = []
    cache: dict = {}
    counted = 0
    for summary in summaries:
        if summary.status not in (RunStatus.FINISHED, RunStatus.FAILED):
            continue
        counted += 1
        steps = store.steps(summary.id)
        leakage, _ = results.score(summary, steps, settings)
        failure = failures.classify(summary, steps, leakage)
        controls, control_steps = _control_runs(store, summary, cache)
        twins = _twin_runs(cache, summary)
        if steps:
            found += inaccessible_controls(steps, leakage)
        found += navigation_failures(summary, steps)
        found += repeated_actions(summary, steps)
        if not catalog.persona(summary.config.persona_id).is_control:
            found += confusing_workflow(summary, steps, control_steps)
        found += failed_task(summary, failure)
        if summary.outcome is not RunOutcome.SUCCESS:
            attributions.append(attribute(summary, steps, leakage, failure, controls, twins))
    return FindingsReport(
        scope=scope,
        runs=counted,
        findings=found,
        attributions=attributions,
        counts=dict(Counter(f.kind.value for f in found)),
        attribution_counts=dict(Counter(a.attribution.value for a in attributions)),
    )


def batch_report(store: RunStore, batch_ids: list[str], settings: Settings) -> FindingsReport:
    summaries = [run for batch_id in batch_ids for run in store.list_runs(batch_id, limit=10_000)]
    return report_for(store, summaries, settings, ", ".join(batch_ids))


def run_report(store: RunStore, run_id: str, settings: Settings) -> FindingsReport | None:
    summary = store.get_run(run_id)
    if summary is None:
        return None
    return report_for(store, [summary], settings, run_id)


KIND_TITLES = {
    FindingKind.INACCESSIBLE_CONTROL: "Controls not reached within the limits",
    FindingKind.NAVIGATION_FAILURE: "Navigation failures",
    FindingKind.REPEATED_ACTIONS: "Repeated actions",
    FindingKind.CONFUSING_WORKFLOW: "Confusing workflows",
    FindingKind.FAILED_TASK: "Failed tasks",
}
ATTRIBUTION_TITLES = {
    Attribution.SITE: "Site (the control fails too)",
    Attribution.RESTRICTION: "Restriction (a barrier for this limit; needs human evaluation)",
    Attribution.AGENT: "Agent (the simulated user's own failure)",
    Attribution.INFRASTRUCTURE: "Infrastructure (model or browser failure)",
    Attribution.UNKNOWN: "Unknown (nothing to compare with)",
}


def markdown(report: FindingsReport, examples: int = 5) -> str:
    lines = [
        f"# Findings: {report.scope}",
        "",
        f"> {LIMITS_STATEMENT}",
        "",
        f"{report.runs} runs; {len(report.findings)} findings; "
        f"{len(report.attributions)} runs did not complete their task.",
        "",
        "## Why runs failed",
        "",
        "| Attribution | Runs |",
        "|---|---|",
    ]
    for kind in Attribution:
        count = report.attribution_counts.get(kind.value, 0)
        if count:
            lines.append(f"| {ATTRIBUTION_TITLES[kind]} | {count} |")
    for item in report.attributions[: examples * 4]:
        lines.append(
            f"- `{item.label}` ({item.outcome}): **{item.attribution.value}**. {item.reason}"
        )
    for kind in FindingKind:
        items = [f for f in report.findings if f.kind is kind]
        if not items:
            continue
        lines += ["", f"## {KIND_TITLES[kind]} ({len(items)})", ""]
        for item in items[:examples]:
            where = (
                f" (run `{item.run_id[:8]}`, steps {', '.join(str(i + 1) for i in item.steps[:8])})"
            )
            lines.append(
                f"- {item.summary}{where if item.steps else f' (run `{item.run_id[:8]}`)'}"
            )
        if len(items) > examples:
            lines.append(f"- and {len(items) - examples} more")
    return "\n".join(lines)
