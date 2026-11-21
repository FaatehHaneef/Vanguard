"""One run: observe -> propose -> gate -> execute -> record, until an end condition.

Every step is written to the store before the next one starts, so a run that crashes
still leaves a complete trace up to the failure.
"""

import time
from datetime import UTC, datetime

from vanguard import verifier as verifier_agent
from vanguard.contracts import (
    Action,
    EnforcementOption,
    GateDecision,
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
from vanguard.providers import ModelRequest, Provider, ProviderUnavailable
from vanguard.providers.tools import all_tool_names
from vanguard.rules import RuleContext
from vanguard.store import RunStore

from .prompts import system_prompt, user_prompt
from .success import answer_success, is_stuck, page_success


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
    history: list[StepRecord] = []
    seen_links: set[str] = set()
    seen_text = "\n".join([task.instruction, *persona.knowledge.knows])
    start_url = site.origin + task.start_path
    system = system_prompt(persona)
    store.mark_running(run_id)

    try:
        await executor.start(site, task, persona)
        for index in range(max_steps):
            observation = await executor.observe()
            seen_links.update(observation.links)
            seen_text += "\n" + observation.content
            request = ModelRequest(
                system=system,
                user=user_prompt(task, history, observation),
                tool_names=all_tool_names(),
                seed=config.seed + index,
            )
            started_at = datetime.now(UTC)
            began = time.perf_counter()
            reply = await provider.next_action(request)
            ctx = RuleContext(
                current_url=observation.url,
                start_url=start_url,
                allowed_origins=allowed_origins,
                seen_links=set(seen_links),
                seen_text=seen_text,
                site_tokens=site.site_tokens,
            )

            action: Action | None = reply.action
            if action is None:
                decision = GateDecision(allowed=False, rule="invalid", message=reply.error)
            else:
                decision = gate.decide(action, ctx)

            verified = None
            if (
                use_verifier
                and action is not None
                and decision.allowed
                and action.tool not in (Tool.DONE, Tool.GIVE_UP)
            ):
                verified = await verifier_agent.verify(provider, action, persona, observation)
                if not verified.allowed:
                    decision = verified

            result = None
            if (
                action is not None
                and decision.allowed
                and action.tool not in (Tool.DONE, Tool.GIVE_UP)
            ):
                result = await executor.execute(action)

            step = StepRecord(
                run_id=run_id,
                index=index,
                started_at=started_at,
                observation=observation,
                proposed=action,
                model_error=reply.error,
                gate=decision,
                verifier=verified,
                executed=result is not None,
                execution_error=result.error if result else None,
                events=result.events if result else [],
                url_after=result.url_after if result else observation.url,
                focus_after=result.focus_after if result else None,
                target_box=result.target_box if result else None,
                latency_ms=(time.perf_counter() - began) * 1000,
                model=reply.model,
                input_tokens=reply.input_tokens,
                output_tokens=reply.output_tokens,
            )
            store.add_step(step)
            history.append(step)

            if action is not None and not decision.allowed:
                await executor.announce(action, decision.message or "Refused", "refused")
            elif action is not None and action.tool is Tool.DONE:
                await executor.announce(action, action.answer or "Done", "done")
            elif action is not None and action.tool is Tool.GIVE_UP:
                await executor.announce(action, action.reason or "Giving up", "refused")

            if action is not None and decision.allowed:
                if action.tool is Tool.DONE:
                    url = await executor.current_url()
                    done_ok = answer_success(task, action) or page_success(
                        task, url, await executor.page_text()
                    )
                    return store.finish_run(
                        run_id, RunOutcome.SUCCESS if done_ok else RunOutcome.GAVE_UP
                    )
                if action.tool is Tool.GIVE_UP:
                    return store.finish_run(run_id, RunOutcome.GAVE_UP)
            if result is not None and page_success(
                task, await executor.current_url(), await executor.page_text()
            ):
                return store.finish_run(run_id, RunOutcome.SUCCESS)
            if is_stuck(history, stuck_after):
                return store.finish_run(run_id, RunOutcome.STUCK)
        return store.finish_run(run_id, RunOutcome.STEP_LIMIT)
    except ProviderUnavailable as error:
        return store.finish_run(run_id, RunOutcome.ERROR, f"model unavailable: {error}")
    except Exception as error:  # recorded, never swallowed silently
        return store.finish_run(run_id, RunOutcome.ERROR, f"{type(error).__name__}: {error}")
    finally:
        await executor.close()
