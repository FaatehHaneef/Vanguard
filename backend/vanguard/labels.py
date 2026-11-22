"""Human labels for the leakage test set (docs/leakage-spec.md, Section 7).

Labellers see a step (the persona, what it perceived, what it proposed, what the gate
did, what the browser recorded) but never the checker's verdict. Two labellers label
the same sampled steps independently; agreement is Cohen's kappa. The checker is then
compared against each labeller, and against the adjudicated label where they agree.

Sampling is deterministic (a seeded shuffle of all finished steps), so every labeller
gets the same items in the same order.
"""

import random
from datetime import UTC, datetime
from enum import StrEnum

from pydantic import BaseModel, Field
from sqlalchemy import DateTime, Integer, String, Text, select
from sqlalchemy.orm import Mapped, mapped_column

from vanguard import catalog
from vanguard.contracts import LimitId, RunStatus, StepRecord
from vanguard.metrics.stats import cohen_kappa, precision_recall
from vanguard.settings import Settings
from vanguard.store import Base, RunStore

SAMPLE_SEED = 4009


class Verdict(StrEnum):
    NO = "no"
    YES = "yes"
    UNSURE = "unsure"


class LeakKind(StrEnum):
    ACTION = "action"
    INFORMATION = "information"


class Label(BaseModel):
    run_id: str
    index: int
    labeller: str = Field(min_length=1, max_length=40)
    verdict: Verdict
    limit: LimitId | None = None
    kind: LeakKind | None = None
    note: str = Field("", max_length=1000)


class LabelRow(Base):
    __tablename__ = "labels"
    run_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    index: Mapped[int] = mapped_column(Integer, primary_key=True)
    labeller: Mapped[str] = mapped_column(String(40), primary_key=True)
    verdict: Mapped[str] = mapped_column(String(8))
    limit: Mapped[str | None] = mapped_column(String(4))
    kind: Mapped[str | None] = mapped_column(String(16))
    note: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class SampleRow(Base):
    """A fixed labelling sample (from a bundle): the order every labeller sees."""

    __tablename__ = "label_samples"
    sample: Mapped[str] = mapped_column(String(64), primary_key=True)
    position: Mapped[int] = mapped_column(Integer, primary_key=True)
    run_id: Mapped[str] = mapped_column(String(32))
    index: Mapped[int] = mapped_column(Integer)


def stored_sample(store: RunStore, name: str) -> list[tuple[str, int]]:
    query = select(SampleRow).where(SampleRow.sample == name).order_by(SampleRow.position)
    with store._session() as session:
        return [(row.run_id, row.index) for row in session.scalars(query)]


class LabelItem(BaseModel):
    """What a labeller sees. Deliberately has no checker output."""

    run_id: str
    index: int
    position: int = Field(description="Position in the shared sample, from 0")
    persona_id: str
    persona_name: str
    persona_limits: list[LimitId]
    persona_description: str
    task: str
    step: StepRecord


def save_label(store: RunStore, label: Label) -> None:
    with store._session() as session, session.begin():
        row = session.get(LabelRow, (label.run_id, label.index, label.labeller))
        values = dict(
            verdict=label.verdict.value,
            limit=label.limit.value if label.limit else None,
            kind=label.kind.value if label.kind else None,
            note=label.note,
            created_at=datetime.now(UTC),
        )
        if row is None:
            session.add(
                LabelRow(run_id=label.run_id, index=label.index, labeller=label.labeller, **values)
            )
        else:
            for key, value in values.items():
                setattr(row, key, value)


def labels(store: RunStore, labeller: str | None = None) -> list[Label]:
    query = select(LabelRow)
    if labeller:
        query = query.where(LabelRow.labeller == labeller)
    with store._session() as session:
        return [
            Label(
                run_id=row.run_id,
                index=row.index,
                labeller=row.labeller,
                verdict=Verdict(row.verdict),
                limit=LimitId(row.limit) if row.limit else None,
                kind=LeakKind(row.kind) if row.kind else None,
                note=row.note,
            )
            for row in session.scalars(query)
        ]


def sample_keys(store: RunStore, batch_id: str | None = None) -> list[tuple[str, int]]:
    """Every step of every finished run, in one fixed shuffled order. A batch imported
    from a labelling bundle uses the bundle's own fixed sample instead."""
    if batch_id:
        fixed = stored_sample(store, batch_id)
        if fixed:
            return fixed
    keys = []
    for run in store.list_runs(batch_id, limit=100_000):
        if run.status is RunStatus.FINISHED:
            keys.extend((run.id, index) for index in range(run.steps))
    keys.sort()
    random.Random(SAMPLE_SEED).shuffle(keys)
    return keys


def next_items(
    store: RunStore, labeller: str, count: int = 10, batch_id: str | None = None
) -> list[LabelItem]:
    done = {(label.run_id, label.index) for label in labels(store, labeller)}
    items = []
    steps_cache: dict[str, list[StepRecord]] = {}
    for position, (run_id, index) in enumerate(sample_keys(store, batch_id)):
        if (run_id, index) in done:
            continue
        run = store.get_run(run_id)
        steps = steps_cache.setdefault(run_id, store.steps(run_id))
        step = next((s for s in steps if s.index == index), None)
        if run is None or step is None:
            continue
        persona = catalog.persona(run.config.persona_id)
        items.append(
            LabelItem(
                run_id=run_id,
                index=index,
                position=position,
                persona_id=persona.id,
                persona_name=persona.name,
                persona_limits=persona.limits,
                persona_description=persona.description,
                task=catalog.task(run.config.task_id).instruction,
                step=step,
            )
        )
        if len(items) >= count:
            break
    return items


def checker_flags(store: RunStore, keys: set[tuple[str, int]]) -> dict[tuple[str, int], bool]:
    """Attempted leakage per step according to the checker, for the given steps.

    Labellers judge the proposal, whether or not it ran (docs/labelling-guide.md: a click
    the gate refused is still "yes"), so the matching checker verdict is *attempted*."""
    from vanguard.results import score  # the same scoring the results tables use

    flags = {}
    for run_id in {run_id for run_id, _ in keys}:
        run = store.get_run(run_id)
        if run is None:
            continue
        leakage, _ = score(run, store.steps(run_id), Settings())
        for verdict in leakage.steps:
            if (run_id, verdict.index) in keys:
                flags[(run_id, verdict.index)] = bool(verdict.attempted)
    return flags


def agreement(store: RunStore, first: str, second: str) -> dict:
    """Labeller vs labeller kappa, and checker vs each labeller and the agreed labels."""
    a = {(lb.run_id, lb.index): lb for lb in labels(store, first)}
    b = {(lb.run_id, lb.index): lb for lb in labels(store, second)}
    both = sorted(set(a) & set(b))
    report: dict = {
        "labellers": [first, second],
        "labelled": {first: len(a), second: len(b)},
        "overlap": len(both),
    }
    if not both:
        return report
    report["kappa"] = cohen_kappa([a[k].verdict for k in both], [b[k].verdict for k in both])
    report["raw_agreement"] = sum(a[k].verdict == b[k].verdict for k in both) / len(both)

    flags = checker_flags(store, set(a) | set(b))
    for name, own in ((first, a), (second, b)):
        sure = [k for k in sorted(own) if own[k].verdict is not Verdict.UNSURE and k in flags]
        human = [own[k].verdict is Verdict.YES for k in sure]
        machine = [flags[k] for k in sure]
        precision, recall = precision_recall(machine, human)
        report[f"checker_vs_{name}"] = {
            "steps": len(sure),
            "kappa": cohen_kappa(machine, human) if sure else 0.0,
            "precision": precision,
            "recall": recall,
        }
    agreed = [k for k in both if a[k].verdict == b[k].verdict != Verdict.UNSURE and k in flags]
    if agreed:
        human = [a[k].verdict is Verdict.YES for k in agreed]
        machine = [flags[k] for k in agreed]
        precision, recall = precision_recall(machine, human)
        report["checker_vs_agreed"] = {
            "steps": len(agreed),
            "kappa": cohen_kappa(machine, human),
            "precision": precision,
            "recall": recall,
        }
    disagreements = [k for k in both if a[k].verdict != b[k].verdict]
    report["disagreements"] = [{"run_id": r, "index": i} for r, i in disagreements]
    return report


def labellers(store: RunStore) -> list[dict]:
    """Everyone who has labelled, with how many steps each."""
    counts: dict[str, int] = {}
    for label in labels(store):
        counts[label.labeller] = counts.get(label.labeller, 0) + 1
    return [{"labeller": name, "labels": count} for name, count in sorted(counts.items())]
