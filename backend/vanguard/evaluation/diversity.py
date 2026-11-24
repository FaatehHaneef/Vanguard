"""Behavioural diversity: how differently personas, and repeated runs of one persona, act.

    python -m vanguard.evaluation diversity --batches <ids...> [--out <file>]

A run's behaviour is the sequence of its proposed actions' types: the tool name, and for
a key press the key too ("press Tab", "press Enter"), since keyboard runs are made of
presses. Refused proposals count: they are what the agent chose.

  (a) Normalised edit distance between two runs' sequences: Levenshtein distance over
      action types divided by the longer sequence's length (0 = the same, 1 = nothing in
      common). Within a persona, the mean over every pair of its runs of the same task;
      between two personas, the mean over every pair of one run of each, same task.
  (b) Shannon entropy (bits) of each persona's action-type mix over all its runs.
  (c) Spread of actions per run and of completion: standard deviation and interquartile
      range across runs for each persona, and across personas of their means.
  (d) Distinct navigation paths: the sequence of URL paths a run visited (repeats in a row
      collapsed), per persona and task.
"""

import argparse
import statistics
from collections import Counter, defaultdict
from dataclasses import dataclass
from itertools import combinations, product
from urllib.parse import urlsplit

from vanguard.contracts import Action, Tool
from vanguard.metrics import percentile
from vanguard.metrics.stats import entropy_bits

from .commands import Command, register
from .data import ScoredRun, add_batch_arguments, load_runs, open_store, write


def action_type(action: Action) -> str:
    if action.tool is Tool.PRESS and action.key:
        return f"press {action.key}"
    return str(action.tool)


def sequence(run: ScoredRun) -> list[str]:
    return [action_type(step.proposed) for step in run.steps if step.proposed is not None]


def edit_distance(a: list[str], b: list[str]) -> int:
    previous = list(range(len(b) + 1))
    for i, item in enumerate(a, start=1):
        current = [i]
        for j, other in enumerate(b, start=1):
            current.append(
                min(previous[j] + 1, current[j - 1] + 1, previous[j - 1] + (item != other))
            )
        previous = current
    return previous[-1]


def normalised_distance(a: list[str], b: list[str]) -> float:
    longest = max(len(a), len(b))
    return edit_distance(a, b) / longest if longest else 0.0


def _mean(values: list[float]) -> float | None:
    return sum(values) / len(values) if values else None


def path(run: ScoredRun) -> tuple[str, ...]:
    urls = [step.observation.url for step in run.steps]
    if run.steps and run.steps[-1].url_after:
        urls.append(run.steps[-1].url_after)
    visited: list[str] = []
    for url in urls:
        page = urlsplit(url).path or "/"
        if not visited or visited[-1] != page:
            visited.append(page)
    return tuple(visited)


@dataclass
class Spread:
    mean: float
    std: float
    iqr: float


def spread(values: list[float]) -> Spread:
    if not values:
        return Spread(0.0, 0.0, 0.0)
    return Spread(
        mean=sum(values) / len(values),
        std=statistics.pstdev(values),
        iqr=percentile(values, 75) - percentile(values, 25),
    )


@dataclass
class Diversity:
    # (task, persona) -> mean pairwise distance within, None with fewer than two runs
    within: dict[tuple[str, str], float | None]
    # (task, persona, persona) -> mean distance between the two personas' runs
    between: dict[tuple[str, str, str], float]
    # persona -> (entropy in bits, distinct action types, actions)
    entropy: dict[str, tuple[float, int, int]]
    actions: dict[str, Spread]  # persona -> actions per run
    completion: dict[str, Spread]  # persona -> completion (0 or 1) per run
    across_actions: Spread  # personas' mean actions
    across_completion: Spread  # personas' completion rates
    paths: dict[tuple[str, str], Counter]  # (task, persona) -> path -> runs


def measure(runs: list[ScoredRun]) -> Diversity:
    by_task: dict[str, dict[str, list[ScoredRun]]] = defaultdict(lambda: defaultdict(list))
    by_persona: dict[str, list[ScoredRun]] = defaultdict(list)
    for run in runs:
        by_task[run.task_id][run.persona_id].append(run)
        by_persona[run.persona_id].append(run)

    within: dict[tuple[str, str], float | None] = {}
    between: dict[tuple[str, str, str], float] = {}
    paths: dict[tuple[str, str], Counter] = {}
    for task, personas in sorted(by_task.items()):
        sequences = {p: [sequence(run) for run in members] for p, members in personas.items()}
        for persona, seqs in sorted(sequences.items()):
            within[(task, persona)] = _mean(
                [normalised_distance(a, b) for a, b in combinations(seqs, 2)]
            )
            paths[(task, persona)] = Counter(path(run) for run in personas[persona])
        for first, second in combinations(sorted(sequences), 2):
            between[(task, first, second)] = (
                _mean(
                    [
                        normalised_distance(a, b)
                        for a, b in product(sequences[first], sequences[second])
                    ]
                )
                or 0.0
            )

    entropy = {}
    actions = {}
    completion = {}
    for persona, members in sorted(by_persona.items()):
        mix = Counter(kind for run in members for kind in sequence(run))
        entropy[persona] = (entropy_bits(mix.values()), len(mix), sum(mix.values()))
        actions[persona] = spread([float(run.metrics.actions) for run in members])
        completion[persona] = spread([float(run.metrics.success) for run in members])
    return Diversity(
        within=within,
        between=between,
        entropy=entropy,
        actions=actions,
        completion=completion,
        across_actions=spread([s.mean for s in actions.values()]),
        across_completion=spread([s.mean for s in completion.values()]),
        paths=paths,
    )


def _number(value: float | None, digits: int = 2) -> str:
    return "-" if value is None else f"{value:.{digits}f}"


def report(d: Diversity, batch_ids: list[str], runs: int, examples: int = 3) -> str:
    lines = [
        "# Behavioural diversity",
        "",
        f"Generated by `python -m vanguard.evaluation diversity` from {runs} finished runs in "
        f"batches {', '.join(f'`{b}`' for b in batch_ids)}.",
        "",
        "A run's behaviour is the sequence of its proposed action types (the tool, and the key "
        "for key presses). Edit distance is the Levenshtein distance between two runs' "
        "sequences divided by the longer one's length: 0 means the same actions in the same "
        "order, 1 nothing in common.",
        "",
    ]
    if not runs:
        lines.append("No finished runs in these batches.")
        return "\n".join(lines) + "\n"
    lines += [
        "## (a) Edit distance within a persona (same task, across runs)",
        "",
        "| task | persona | mean distance |",
        "|---|---|---|",
    ]
    lines += [f"| `{t}` | {p} | {_number(v)} |" for (t, p), v in d.within.items()]
    lines += ["", "## (a) Edit distance between personas (same task)", ""]
    if d.between:
        lines += ["| task | personas | mean distance |", "|---|---|---|"]
        lines += [f"| `{t}` | {a} vs {b} | {_number(v)} |" for (t, a, b), v in d.between.items()]
    else:
        lines.append("No task was run by more than one persona.")
    lines += [
        "",
        "## (b) Entropy of the action-type mix",
        "",
        "| persona | entropy (bits) | distinct action types | actions |",
        "|---|---|---|---|",
    ]
    lines += [f"| {p} | {e:.2f} | {k} | {n} |" for p, (e, k, n) in d.entropy.items()]
    lines += [
        "",
        "## (c) Spread of actions and completion",
        "",
        "| persona | actions per run: mean / std / IQR | completion: rate / std |",
        "|---|---|---|",
    ]
    for persona, act in d.actions.items():
        done = d.completion[persona]
        lines.append(
            f"| {persona} | {act.mean:.1f} / {act.std:.1f} / {act.iqr:.1f} "
            f"| {done.mean:.0%} / {done.std:.2f} |"
        )
    lines += [
        f"| **across personas** | {d.across_actions.mean:.1f} / {d.across_actions.std:.1f} / "
        f"{d.across_actions.iqr:.1f} | {d.across_completion.mean:.0%} / "
        f"{d.across_completion.std:.2f} |",
        "",
        "## (d) Distinct navigation paths",
        "",
        f"| task | persona | runs | distinct paths | most common (up to {examples}) |",
        "|---|---|---|---|---|",
    ]
    for (task, persona), counter in d.paths.items():
        common = "; ".join(f"{' → '.join(p)} ({n})" for p, n in counter.most_common(examples))
        lines.append(
            f"| `{task}` | {persona} | {sum(counter.values())} | {len(counter)} | {common} |"
        )
    return "\n".join(lines) + "\n"


def _add_arguments(parser: argparse.ArgumentParser) -> None:
    add_batch_arguments(parser, "diversity.md")


def _run(args: argparse.Namespace) -> int:
    store, settings = open_store()
    runs = load_runs(store, args.batches, settings)
    write(args.out, report(measure(runs), args.batches, len(runs)))
    return 0


register(
    Command(
        "diversity",
        "Measure how differently personas and repeated runs behave.",
        _add_arguments,
        _run,
    )
)
