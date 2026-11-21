"""The trace store: runs and their step records.

Postgres in Docker, SQLite for tests and quick local use. Step records are stored as
JSON exactly as the StepRecord contract defines them, so the checker, the labelling
workspace and the results scripts all read the same thing. Records are append-only:
a step is never edited after it is written.
"""

import uuid
from datetime import UTC, datetime

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, Text, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

from vanguard.contracts import RunConfig, RunOutcome, RunStatus, RunSummary, StepRecord


class Base(DeclarativeBase):
    pass


class RunRow(Base):
    __tablename__ = "runs"
    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    batch_id: Mapped[str | None] = mapped_column(String(32), index=True)
    label: Mapped[str] = mapped_column(String(200))
    config: Mapped[dict] = mapped_column(JSON)
    status: Mapped[str] = mapped_column(String(16), index=True)
    outcome: Mapped[str | None] = mapped_column(String(16))
    steps: Mapped[int] = mapped_column(Integer, default=0)
    blocked: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    error: Mapped[str | None] = mapped_column(Text)


class StepRow(Base):
    __tablename__ = "steps"
    run_id: Mapped[str] = mapped_column(ForeignKey("runs.id"), primary_key=True)
    index: Mapped[int] = mapped_column(Integer, primary_key=True)
    record: Mapped[dict] = mapped_column(JSON)


def _now() -> datetime:
    return datetime.now(UTC)


def _summary(row: RunRow) -> RunSummary:
    return RunSummary(
        id=row.id,
        config=RunConfig.model_validate(row.config),
        status=RunStatus(row.status),
        outcome=RunOutcome(row.outcome) if row.outcome else None,
        steps=row.steps,
        blocked=row.blocked,
        created_at=row.created_at,
        finished_at=row.finished_at,
        error=row.error,
    )


class RunStore:
    def __init__(self, database_url: str):
        connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}
        self.engine = create_engine(database_url, connect_args=connect_args)
        self._sessions = sessionmaker(self.engine, expire_on_commit=False)

    def create_schema(self) -> None:
        Base.metadata.create_all(self.engine)

    def _session(self) -> Session:
        return self._sessions()

    def create_run(self, config: RunConfig) -> RunSummary:
        row = RunRow(
            id=uuid.uuid4().hex,
            batch_id=config.batch_id,
            label=config.label(),
            config=config.model_dump(mode="json"),
            status=RunStatus.QUEUED,
            created_at=_now(),
        )
        with self._session() as session, session.begin():
            session.add(row)
        return _summary(row)

    def mark_running(self, run_id: str) -> None:
        with self._session() as session, session.begin():
            session.get(RunRow, run_id).status = RunStatus.RUNNING

    def add_step(self, step: StepRecord) -> None:
        with self._session() as session, session.begin():
            session.add(StepRow(run_id=step.run_id, index=step.index, record=step.model_dump(mode="json")))
            run = session.get(RunRow, step.run_id)
            run.steps += 1
            if not step.gate.allowed and step.proposed is not None:  # unusable replies are not blocks
                run.blocked += 1

    def finish_run(self, run_id: str, outcome: RunOutcome, error: str | None = None) -> RunSummary:
        with self._session() as session, session.begin():
            row = session.get(RunRow, run_id)
            row.status = RunStatus.FAILED if outcome is RunOutcome.ERROR else RunStatus.FINISHED
            row.outcome = outcome
            row.error = error
            row.finished_at = _now()
        return self.get_run(run_id)

    def get_run(self, run_id: str) -> RunSummary | None:
        with self._session() as session:
            row = session.get(RunRow, run_id)
            return _summary(row) if row else None

    def list_runs(self, batch_id: str | None = None, limit: int = 100) -> list[RunSummary]:
        query = select(RunRow).order_by(RunRow.created_at.desc()).limit(limit)
        if batch_id:
            query = query.where(RunRow.batch_id == batch_id)
        with self._session() as session:
            return [_summary(row) for row in session.scalars(query)]

    def steps(self, run_id: str) -> list[StepRecord]:
        query = select(StepRow).where(StepRow.run_id == run_id).order_by(StepRow.index)
        with self._session() as session:
            return [StepRecord.model_validate(row.record) for row in session.scalars(query)]
