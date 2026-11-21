import asyncio

import pytest
from test_api import client  # noqa: F401  (fixture)

from vanguard import batch
from vanguard.contracts import BatchRequest
from vanguard.settings import Settings
from vanguard.store import RunStore


@pytest.fixture
def setup(tmp_path):
    settings = Settings(
        database_url=f"sqlite:///{tmp_path / 'b.db'}",
        executor="fake",
        enabled_providers=["fake"],
        screenshots=False,
    )
    store = RunStore(settings.database_url)
    store.create_schema()
    return settings, store


def request(**overrides) -> BatchRequest:
    body = dict(
        site_id="tallowmere",
        task_ids=["buy-one"],
        persona_ids=["keyboard-only", "unrestricted"],
        provider="fake",
        repeats=2,
        max_steps=6,
    )
    body.update(overrides)
    return BatchRequest(**body)


def test_batch_runs_every_group_and_resumes(setup):
    settings, store = setup
    req = batch.prepare(request(), settings)
    partial = asyncio.run(batch.run_batch(req, settings, store, max_runs=3))
    assert partial.stopped == "run cap reached" and partial.remaining == 5
    # Balanced: the three runs went to three different groups.
    assert sorted(g.done for g in partial.groups) == [0, 1, 1, 1]
    final = asyncio.run(batch.run_batch(req, settings, store))
    assert final.remaining == 0 and final.stopped is None
    assert all(g.done == 2 for g in final.groups)
    assert len(store.list_runs(req.batch_id)) == 8  # nothing repeated


def test_preview_persona_with_gate_is_rejected_before_running(setup):
    settings, store = setup
    from vanguard.service import RunRejected

    with pytest.raises(RunRejected):
        batch.prepare(request(persona_ids=["screen-reader"]), settings)
    assert store.list_runs() == []


def test_batch_api(client):  # noqa: F811
    body = request().model_dump(mode="json")
    created = client.post("/batches", json=body)
    assert created.status_code == 202
    batch_id = created.json()["batch_id"]
    status = client.get(f"/batches/{batch_id}").json()
    assert status["remaining"] == 0
    assert [b["batch_id"] for b in client.get("/batches").json()] == [batch_id]
    assert len(client.get(f"/batches/{batch_id}/metrics").json()) == 4
    assert client.get("/batches/nope").status_code == 404
