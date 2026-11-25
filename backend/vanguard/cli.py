"""Command line for running and inspecting trials without the web app.

    python -m vanguard.cli run --persona keyboard-only --task buy-two --enforcement gate
    python -m vanguard.cli run --persona keyboard-only --task buy-two --enforcement prompt_only \
        --repeats 3 --batch knock-buy-two
    python -m vanguard.cli show <run_id>
    python -m vanguard.cli batch --personas keyboard-only unrestricted --tasks buy-two \
        --repeats 5 --batch a3-baseline   # prompt_only and gate, balanced, resumable
    python -m vanguard.cli usage                              # model calls left today
    python -m vanguard.cli batch ... --max-calls 80           # stop before the budget runs out
    python -m vanguard.cli failures --batch a3-baseline     # failing runs grouped by cause
    python -m vanguard.cli findings --batches a3-baseline [--out findings.md]  # usability
    python -m vanguard.cli check-site willowbrook --dir sites/willowbrook-clinic --live
    python -m vanguard.cli labelling export --batches a3-tallowmere a3-willowbrook --name a3
    python -m vanguard.cli labelling import data/labelling/a3
    python -m vanguard.cli labelling export-labels --labeller hadi
    python -m vanguard.cli labelling import-labels data/labels/hadi.json data/labels/ibrahim.json
    python -m vanguard.cli report --batch knock-buy-two [--out results.md]

Settings come from the environment and .env, as for the API (VANGUARD_EXECUTOR,
VANGUARD_DATABASE_URL, VANGUARD_GEMINI_API_KEYS, ...).
"""

import argparse
import asyncio
import sys
from pathlib import Path

from vanguard import (
    batch,
    bundle,
    deps,
    failures,
    findings,
    results,
    service,
    sitecheck,
    usage,
)
from vanguard.contracts import BatchRequest, EnforcementOption, RunConfig, StepRecord
from vanguard.settings import REPO_ROOT, get_settings
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
    store = deps.open_store(settings)
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
            actions_per_call=args.actions_per_call,
            batch_id=args.batch,
        )
        summary = service.create(config, settings, store)
        await service.execute(summary.id, summary.config, settings, store)
        _print_run(store, summary.id)
    return 0


async def _batch(args: argparse.Namespace) -> int:
    settings = get_settings()
    store = deps.open_store(settings)
    request = BatchRequest(
        batch_id=args.batch,
        site_id=args.site,
        task_ids=args.tasks,
        persona_ids=args.personas,
        enforcements=[
            [EnforcementOption(part) for part in option.split("+")] for option in args.enforcements
        ],
        provider=args.provider or settings.default_provider,
        repeats=args.repeats,
        max_steps=args.max_steps,
        actions_per_call=args.actions_per_call,
        max_calls=args.max_calls,
    )
    request = batch.prepare(request, settings)
    store.save_batch(request)
    print(f"batch {request.batch_id}")
    final = await batch.run_batch(request, settings, store, max_runs=args.max_runs)
    for group in final.groups:
        options = "+".join(group.enforcement)
        print(f"  {group.persona_id}/{group.task_id}/{options}: {group.done}/{group.target}")
    if final.stopped:
        print(f"stopped: {final.stopped}")
    print(results.markdown_table(results.batch_groups(store, request.batch_id, settings)))
    return 0 if final.remaining == 0 else 1


def _labelling(args: argparse.Namespace) -> int:
    settings = get_settings()
    store = deps.open_store(settings)
    data = REPO_ROOT / "data"
    if args.action == "export":
        result = bundle.export_bundle(
            store,
            args.batches,
            data / "labelling" / args.name,
            args.name,
            args.count,
            frozenset(args.no_shots),
        )
        print(f"bundle {result['name']}: {result['items']} steps from {result['runs']} runs")
    elif args.action == "import":
        folder = args.folder if args.folder.is_absolute() else REPO_ROOT / args.folder
        result = bundle.import_bundle(store, folder, settings)
        print(f"imported {result['items']} steps; label at /labelling?batch={result['batch_id']}")
    elif args.action == "export-labels":
        out = data / "labels" / f"{args.labeller}.json"
        count = bundle.export_labels(store, args.labeller, out)
        print(f"wrote {count} labels to {out.relative_to(REPO_ROOT)}")
    else:
        files = [f if f.is_absolute() else REPO_ROOT / f for f in args.files]
        print(f"imported {bundle.import_labels(store, files)} labels")
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
    run.add_argument(
        "--actions-per-call", type=int, default=None, help="default: VANGUARD_ACTIONS_PER_CALL"
    )
    run.add_argument("--batch", default=None)

    show = sub.add_parser("show", help="print a run and its steps")
    show.add_argument("run_id")

    many = sub.add_parser("batch", help="run a balanced, resumable batch")
    many.add_argument("--site", default="tallowmere")
    many.add_argument("--tasks", nargs="+", required=True)
    many.add_argument("--personas", nargs="+", required=True)
    many.add_argument(
        "--enforcements",
        nargs="+",
        default=["prompt_only", "gate"],
        help="one option per configuration; join combined options with +, e.g. gate+verifier",
    )
    many.add_argument("--provider", default=None)
    many.add_argument("--repeats", type=int, default=3)
    many.add_argument("--max-steps", type=int, default=None)
    many.add_argument("--max-runs", type=int, default=None)
    many.add_argument(
        "--max-calls",
        type=int,
        default=None,
        help="stop before a run that could go past this many model calls (see `usage`)",
    )
    many.add_argument("--actions-per-call", type=int, default=None)
    many.add_argument("--batch", default=None)

    failing = sub.add_parser("failures", help="failing runs grouped by cause")
    failing.add_argument("--batch", default=None)
    failing.add_argument("--out", type=Path, default=None)

    site_check = sub.add_parser("check-site", help="check a test site against the kit")
    site_check.add_argument("site_id")
    site_check.add_argument("--dir", type=Path, required=True, help="the site's folder")
    site_check.add_argument("--live", action="store_true", help="also request its pages")
    lab = sub.add_parser("labelling", help="labelling bundles and label files")
    lab_sub = lab.add_subparsers(dest="action", required=True)
    exp = lab_sub.add_parser("export", help="write a labelling bundle from finished batches")
    exp.add_argument("--batches", nargs="+", required=True)
    exp.add_argument("--name", required=True)
    exp.add_argument("--count", type=int, default=60)
    exp.add_argument(
        "--no-shots", nargs="*", default=[], help="batches to export without screenshots"
    )
    imp = lab_sub.add_parser("import", help="load a labelling bundle into the local store")
    imp.add_argument("folder", type=Path)
    exl = lab_sub.add_parser("export-labels", help="write your labels to data/labels/")
    exl.add_argument("--labeller", required=True)
    iml = lab_sub.add_parser("import-labels", help="load label files")
    iml.add_argument("files", nargs="+", type=Path)

    sub.add_parser("usage", help="model calls made today against today's budget")

    found = sub.add_parser("findings", help="usability findings and failure attribution")
    found.add_argument("--batches", nargs="+", required=True)
    found.add_argument("--out", type=Path, default=None)

    report = sub.add_parser("report", help="metrics table for a batch (or all runs)")
    report.add_argument("--batch", default=None)
    report.add_argument("--out", type=Path, default=None)

    args = parser.parse_args(argv)
    if args.command == "batch":
        return asyncio.run(_batch(args))
    if args.command == "labelling":
        return _labelling(args)
    if args.command == "check-site":
        folder = args.dir if args.dir.is_absolute() else REPO_ROOT / args.dir
        checks = sitecheck.run_checks(args.site_id, folder, live=args.live)
        print(sitecheck.report(checks))
        return 0 if all(check.ok for check in checks) else 1
    if args.command == "failures":
        settings = get_settings()
        items = results.batch_failures(deps.open_store(settings), args.batch, settings)
        table = failures.markdown(items)
        if args.out:
            args.out.write_text(table + "\n", encoding="utf-8")
        print(table)
        return 0
    if args.command == "report":
        settings = get_settings()
        groups = results.batch_groups(deps.open_store(settings), args.batch, settings)
        table = results.markdown_table(groups)
        if args.out:
            args.out.write_text(table + "\n", encoding="utf-8")
        print(table)
        return 0
    if args.command == "findings":
        settings = get_settings()
        report = findings.batch_report(deps.open_store(settings), args.batches, settings)
        text = findings.markdown(report)
        if args.out:
            args.out.write_text(text + "\n", encoding="utf-8")
        print(text)
        return 0
    if args.command == "usage":
        settings = get_settings()
        store = deps.open_store(settings)
        print(usage.report(usage.usage_since(store, usage.quota_day_start()), settings))
        return 0
    if args.command == "show":
        settings = get_settings()
        _print_run(deps.open_store(settings), args.run_id)
        return 0
    args.provider = args.provider or get_settings().default_provider
    return asyncio.run(_run(args))


if __name__ == "__main__":
    sys.exit(main())
