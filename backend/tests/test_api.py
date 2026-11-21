import pytest
from fastapi.testclient import TestClient

from vanguard.settings import get_settings


@pytest.fixture
def client(monkeypatch, tmp_path):
    monkeypatch.setenv("VANGUARD_DATABASE_URL", f"sqlite:///{tmp_path / 'test.db'}")
    monkeypatch.setenv("VANGUARD_EXECUTOR", "fake")
    monkeypatch.setenv("VANGUARD_ENABLED_PROVIDERS", '["fake"]')
    get_settings.cache_clear()
    from vanguard.api import app

    with TestClient(app) as client:
        yield client
    get_settings.cache_clear()


def test_health_and_catalog(client):
    assert client.get("/health").json()["status"] == "ok"
    assert len(client.get("/personas").json()) == 5
    assert [task["id"] for task in client.get("/sites/tallowmere/tasks").json()]
    assert client.get("/sites/nowhere/tasks").status_code == 404


def test_run_lifecycle(client):
    body = {
        "site_id": "tallowmere",
        "task_id": "buy-one",
        "persona_id": "keyboard-only",
        "enforcement": ["gate"],
        "provider": "fake",
    }
    created = client.post("/runs", json=body)
    assert created.status_code == 202
    run_id = created.json()["id"]
    # TestClient runs background tasks before returning, so the run is finished here.
    summary = client.get(f"/runs/{run_id}").json()
    assert summary["status"] == "finished"
    assert client.get(f"/runs/{run_id}/steps").json()


def test_preview_persona_rejects_gate(client):
    body = {
        "site_id": "tallowmere",
        "task_id": "buy-one",
        "persona_id": "screen-reader",
        "enforcement": ["gate"],
        "provider": "fake",
    }
    assert client.post("/runs", json=body).status_code == 422


def test_task_must_match_site(client):
    body = {
        "site_id": "elsewhere",
        "task_id": "buy-one",
        "persona_id": "keyboard-only",
        "provider": "fake",
    }
    assert client.post("/runs", json=body).status_code == 422


def test_report_and_batch_metrics(client):
    body = {
        "site_id": "tallowmere",
        "task_id": "buy-one",
        "persona_id": "keyboard-only",
        "enforcement": ["gate"],
        "provider": "fake",
        "batch_id": "b1",
    }
    run_id = client.post("/runs", json=body).json()["id"]
    report = client.get(f"/runs/{run_id}/report").json()
    assert report["metrics"]["executed_leak_steps"] == 0
    assert len(report["steps"]) == report["metrics"]["steps"]
    groups = client.get("/batches/b1/metrics").json()
    assert [g["key"] for g in groups] == ["keyboard-only/buy-one/gate/fake"]
    assert client.get("/runs/nope/report").status_code == 404
    # The fake executor takes no screenshots.
    assert client.get(f"/runs/{run_id}/steps/0/screenshot").status_code == 404


def test_sites_do_not_expose_the_test_manifest(client):
    body = client.get("/sites").text
    assert "honeytokens" not in body and "TMX-5521" not in body and "site_tokens" not in body
