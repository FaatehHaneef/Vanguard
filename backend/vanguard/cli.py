"""Command line for running and inspecting trials without the web app.

    python -m vanguard.cli run --persona keyboard-only --task buy-two --enforcement gate
    python -m vanguard.cli run --persona keyboard-only --task buy-two --enforcement prompt_only \
        --repeats 3 --batch knock-buy-two
    python -m vanguard.cli show <run_id>
    python -m vanguard.cli report --batch knock-buy-two [--out results.md]

Settings come from the environment and .env, as for the API (VANGUARD_EXECUTOR,
VANGUARD_DATABASE_URL, VANGUARD_GEMINI_API_KEYS, ...).
"""

import argparse
import asyncio
import sys
from pathlib import Path

from vanguard import results, service
from vanguard.contracts import EnforcementOption, RunConfig, StepRecord
from vanguard.settings import get_settings
from vanguard.store import RunStore


def _step_line(step: StepRecord) -> str:
    action = step.proposed
    if action is None:
        what = f"(invalid: {step.model_error})"
    else:
        args = action.model_dump(exclude={"tool", "rationale"}, exclude_none=True)
        what = f"{action.tool}({', '.join(f'{k}={v!r}' for k, v in args.items())})"
    if not step.gate.allowed:
        verdict = f"BLOCKED {step.gate.rule}"
    elif step.execution_error:
        verdict = f"failed: {step.execution_error}"
    else:
        verdict = "ok"
    pointer = sum(
        e.trusted and e.type in ("pointerdown", "mousedown", "wheel") for e in step.events
    )
    extra = f" pointer_events={pointer}" if pointer else ""
    return f"  {step.index + 1:>2}. {what} -> {verdict}{extra} [{step.latency_ms:.0f} ms]"


def _print_run(store: RunStore, run_id: str) -> None:
    run = store.get_run(run_id)
    if run is None:
        print(f"no run {run_id}")
        return
    print(f"{run.id} {run.config.label()} {run.status} outcome={run.outcome} steps={run.steps}")
    for step in store.steps(run_id):
        print(_step_line(step))
        if step.proposed is not None and step.proposed.rationale:
            print(f"      why: {step.proposed.rationale}")
    if run.error:
        print(f"  error: {run.error}")


async def _run(args: argparse.Namespace) -> int:
    settings = get_settings()
    store = RunStore(settings.database_url)
    store.create_schema()
    for repeat in range(args.repeats):
        config = RunConfig(
            site_id=args.site,
            task_id=args.task,
            persona_id=args.persona,
            enforcement=[EnforcementOption(option) for option in args.enforcement],
            provider=args.provider,
            seed=args.seed + repeat,
            repeat_index=repeat,
            max_steps=args.max_steps,
            batch_id=args.batch,
        )
        summary = service.create(config, settings, store)
        await service.execute(summary.id, config, settings, store)
        _print_run(store, summary.id)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="vanguard")
    sub = parser.add_subparsers(dest="command", required=True)

    run = sub.add_parser("run", help="run one or more trials")
    run.add_argument("--site", default="tallowmere")
    run.add_argument("--task", required=True)
    run.add_argument("--persona", required=True)
    run.add_argument(
        "--enforcement",
        nargs="+",
        default=["prompt_only"],
        choices=[option.value for option in EnforcementOption],
    )
    run.add_argument("--provider", default=None)
    run.add_argument("--repeats", type=int, default=1)
    run.add_argument("--seed", type=int, default=0)
    run.add_argument("--max-steps", type=int, default=None)
    run.add_argument("--batch", default=None)

    show = sub.add_parser("show", help="print a run and its steps")
    show.add_argument("run_id")

    report = sub.add_parser("report", help="metrics table for a batch (or all runs)")
    report.add_argument("--batch", default=None)
    report.add_argument("--out", type=Path, default=None)

    args = parser.parse_args(argv)
    if args.command == "report":
        settings = get_settings()
        groups = results.batch_groups(RunStore(settings.database_url), args.batch, settings)
        table = results.markdown_table(groups)
        if args.out:
            args.out.write_text(table + "\n", encoding="utf-8")
        print(table)
        return 0
    if args.command == "show":
        settings = get_settings()
        _print_run(RunStore(settings.database_url), args.run_id)
        return 0
    args.provider = args.provider or get_settings().default_provider
    return asyncio.run(_run(args))


if __name__ == "__main__":
    sys.exit(main())
