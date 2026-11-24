"""One run: observe -> propose -> gate -> execute -> record, until an end condition.

The model may return several actions in one call (RunConfig.actions_per_call). Each one
is its own step: gated, verified and executed in order, and recorded with its call
number and position. The rest of a call is dropped at the first refused, invalid or
failed action, when the page address changes, or when a planned element is no longer
on the page; the model then sees the page again.

Every step is written to the store before the next one starts, so a run that crashes
still leaves a complete trace up to the failure.
"""

import time
from dataclasses import dataclass
from datetime import UTC, datetime

from vanguard import verifier as verifier_agent
from vanguard.contracts import (
    Action,
    EnforcementOption,
    GateDecision,
    Observation,
    PersonaSpec,
    RunConfig,
    RunOutcome,
    RunSummary,
    Site,
    StepRecord,
    Task,
    Tool,
)
from vanguard.executor import Executor
from vanguard.gate import ActionGate
from vanguard.providers import ModelReply, ModelRequest, Provider, ProviderUnavailable
from vanguard.providers.tools import all_tool_names
from vanguard.rules import RuleContext
from vanguard.store import RunStore

from .prompts import system_prompt, user_prompt
from .success import answer_success, is_stuck, page_success

END_TOOLS = (Tool.DONE, Tool.GIVE_UP)


async def run_once(
    run_id: str,
    config: RunConfig,
    persona: PersonaSpec,
    site: Site,
    task: Task,
    provider: Provider,
    executor: Executor,
    store: RunStore,
    *,
    allowed_origins: list[str],
    max_steps: int,
    stuck_after: int,
) -> RunSummary:
    gate = ActionGate(persona, config.enforcement)
    use_verifier = EnforcementOption.VERIFIER in config.enforcement
    per_call = config.actions_per_call or 1
    history: list[StepRecord] = []
    seen_links: set[str] = set()
    seen_text = "\n".join([task.instruction, *persona.knowledge.knows])
    start_url = site.origin + task.start_path
    system = system_prompt(persona, per_call)
    store.mark_running(run_id)

    try:
        await executor.start(site, task, persona)
        index = 0
        call = 0
        while index < max_steps:
            # What the persona perceives: only observations shown to the model count.
            observation = await executor.observe()
            seen_links.update(observation.links)
            seen_text += "\n" + observation.content
            request = ModelRequest(
                system=system,
                user=user_prompt(task, history, observation),
                tool_names=all_tool_names(),
                seed=config.seed + call,
                max_actions=per_call,
            )
            started_at = datetime.now(UTC)
            began = time.perf_counter()
            reply = await provider.next_action(request)
            actions: list[Action | None] = list(reply.actions) or [reply.action]

            for position, action in enumerate(actions):
                if index >= max_steps:
                    break
                if position > 0:
                    # The state this action acts on. It is recorded, but it was never shown
                    # to the model, so it adds nothing to what the persona has seen.
                    observation = await executor.observe()
                    if not _refs_present(action, observation):
                        break  # planned on an element that is gone: ask the model again
                    started_at = datetime.now(UTC)
                    began = time.perf_counter()
                ctx = RuleContext(
                    current_url=observation.url,
                    start_url=start_url,
                    allowed_origins=allowed_origins,
                    seen_links=set(seen_links),
                    seen_text=seen_text,
                    site_tokens=site.site_tokens,
                )
                step, result = await _step(
                    StepInput(run_id, index, call, position, started_at, began, observation),
                    action,
                    reply,
                    gate,
                    ctx,
                    provider if use_verifier else None,
                    persona,
                    executor,
                )
                store.add_step(step)
                history.append(step)
                index += 1

                outcome = await _outcome(step, result, task, executor, history, stuck_after)
                if outcome is not None:
                    return store.finish_run(run_id, outcome)
                if not _continue_call(step):
                    break
            call += 1
        return store.finish_run(run_id, RunOutcome.STEP_LIMIT)
    except ProviderUnavailable as error:
        return store.finish_run(run_id, RunOutcome.ERROR, f"model unavailable: {error}")
    except Exception as error:  # recorded, never swallowed silently
        return store.finish_run(run_id, RunOutcome.ERROR, f"{type(error).__name__}: {error}")
    finally:
        await executor.close()


def _refs_present(action: Action | None, observation: Observation) -> bool:
    """A later action of a call may only use element ids that are still on the page."""
    if action is None:
        return False
    refs = [ref for ref in (action.ref, action.to_ref) if ref]
    return all(f"[{ref}]" in observation.content for ref in refs)


def _continue_call(step: StepRecord) -> bool:
    """The rest of a call runs only after an action that was allowed, ran without error
    and left the page at the same address."""
    return (
        step.proposed is not None
        and step.gate.allowed
        and step.executed
        and step.execution_error is None
        and step.url_after == step.observation.url
    )


@dataclass
class StepInput:
    """Where a step sits in the run and what it acts on."""

    run_id: str
    index: int
    call: int
    position: int
    started_at: datetime
    began: float
    observation: Observation


async def _step(
    where: StepInput,
    action: Action | None,
    reply: ModelReply,
    gate: ActionGate,
    ctx: RuleContext,
    verifier: Provider | None,
    persona: PersonaSpec,
    executor: Executor,
):
    """Gate, verify and execute one action; return its record and the execution result."""
    observation = where.observation
    if action is None:
        decision = GateDecision(allowed=False, rule="invalid", message=reply.error)
    else:
        decision = gate.decide(action, ctx)

    verified = None
    if verifier and action is not None and decision.allowed and action.tool not in END_TOOLS:
        verified = await verifier_agent.verify(verifier, action, persona, observation)
        if not verified.allowed:
            decision = verified

    result = None
    if action is not None and decision.allowed and action.tool not in END_TOOLS:
        result = await executor.execute(action)

    first = where.position == 0  # the call's tokens are recorded on its first step
    step = StepRecord(
        run_id=where.run_id,
        index=where.index,
        started_at=where.started_at,
        observation=observation,
        proposed=action,
        model_error=reply.error if first else None,
        gate=decision,
        verifier=verified,
        executed=result is not None,
        execution_error=result.error if result else None,
        events=result.events if result else [],
        url_after=result.url_after if result else observation.url,
        focus_after=result.focus_after if result else None,
        target_box=result.target_box if result else None,
        call=where.call,
        in_call=where.position,
        latency_ms=(time.perf_counter() - where.began) * 1000,
        model=reply.model,
        input_tokens=reply.input_tokens if first else 0,
        output_tokens=reply.output_tokens if first else 0,
    )

    if action is not None and not decision.allowed:
        await executor.announce(action, decision.message or "Refused", "refused")
    elif action is not None and action.tool is Tool.DONE:
        await executor.announce(action, action.answer or "Done", "done")
    elif action is not None and action.tool is Tool.GIVE_UP:
        await executor.announce(action, action.reason or "Giving up", "refused")
    return step, result


async def _outcome(
    step: StepRecord,
    result,
    task: Task,
    executor: Executor,
    history: list[StepRecord],
    stuck_after: int,
) -> RunOutcome | None:
    """How the run ends after this step, or None when it goes on."""
    action = step.proposed
    if action is not None and step.gate.allowed:
        if action.tool is Tool.DONE:
            url = await executor.current_url()
            done_ok = answer_success(task, action) or page_success(
                task, url, await executor.page_text()
            )
            return RunOutcome.SUCCESS if done_ok else RunOutcome.GAVE_UP
        if action.tool is Tool.GIVE_UP:
            return RunOutcome.GAVE_UP
    if result is not None and page_success(
        task, await executor.current_url(), await executor.page_text()
    ):
        return RunOutcome.SUCCESS
    if is_stuck(history, stuck_after):
        return RunOutcome.STUCK
    return None
