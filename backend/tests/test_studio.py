"""The configuration studio: custom personas, sites and tasks (vanguard.studio)."""

import pytest
from fastapi.testclient import TestClient

from vanguard import catalog, deps
from vanguard.settings import get_settings

PERSONA = {
    "name": "Slow Knock",
    "character": "knock",
    "represents": "A shopper who uses only a keyboard and reads every page twice",
    "description": "You use only a keyboard and take your time on every page.",
    "limits": ["L1"],
    "perception": "full",
    "tool_groups": ["keyboard", "navigation", "control"],
    "knowledge": {"knows": ["general web conventions"], "does_not_know": []},
}
SITE = {"name": "Corner shop", "origin": "http://localhost:3999/", "description": "A small shop."}


@pytest.fixture
def client(monkeypatch, tmp_path):
    monkeypatch.setenv("VANGUARD_DATABASE_URL", f"sqlite:///{tmp_path / 'studio.db'}")
    monkeypatch.setenv("VANGUARD_EXECUTOR", "fake")
    monkeypatch.setenv("VANGUARD_ENABLED_PROVIDERS", '["fake"]')
    # The API opens its own store; put the previous one back afterwards, so later tests
    # never see this test's custom items.
    monkeypatch.setattr(deps, "_store", None)
    get_settings.cache_clear()
    from vanguard.api import app

    with TestClient(app) as client:
        yield client
    get_settings.cache_clear()


def make_site(client, **changes) -> dict:
    response = client.post("/studio/sites", json={**SITE, **changes})
    assert response.status_code == 201, response.text
    return response.json()


def make_task(client, site_id: str, **changes) -> dict:
    body = {
        "site_id": site_id,
        "instruction": "Buy one Dusk Ember candle.",
        "scenario": "checkout",
        "start_path": "/",
        "success": {"url_prefix": "/thanks"},
        **changes,
    }
    response = client.post("/studio/tasks", json=body)
    assert response.status_code == 201, response.text
    return response.json()


def message(response) -> str:
    return " ".join(item["msg"] for item in response.json()["detail"])


# ---------------------------------------------------------------- personas


def test_create_edit_list_and_delete_a_persona(client):
    created = client.post("/studio/personas", json=PERSONA)
    assert created.status_code == 201
    persona = created.json()
    assert persona["id"].startswith("custom-slow-knock-")
    assert len(persona["id"].rsplit("-", 1)[1]) == 4

    assert [p["id"] for p in client.get("/studio/personas").json()] == [persona["id"]]
    assert client.get(f"/studio/personas/{persona['id']}").json()["name"] == "Slow Knock"

    edited = client.put(
        f"/studio/personas/{persona['id']}", json={**PERSONA, "name": "Patient Knock"}
    )
    assert edited.status_code == 200
    assert edited.json()["id"] == persona["id"]
    assert client.get(f"/studio/personas/{persona['id']}").json()["name"] == "Patient Knock"

    assert client.delete(f"/studio/personas/{persona['id']}").status_code == 204
    assert client.get("/studio/personas").json() == []
    assert client.get(f"/studio/personas/{persona['id']}").status_code == 404
    assert client.delete(f"/studio/personas/{persona['id']}").status_code == 404


def test_a_custom_persona_joins_the_catalog(client):
    persona = client.post("/studio/personas", json=PERSONA).json()
    assert persona["id"] in catalog.personas()
    assert persona["id"] in {p["id"] for p in client.get("/personas").json()}
    # Built-in personas are still all there.
    assert set(catalog.builtin_personas()) <= set(catalog.personas())


def test_status_is_full_only_for_a_validated_bundle(client):
    # The same limits, perception and tools as Knock (a full built-in persona): full.
    assert client.post("/studio/personas", json=PERSONA).json()["status"] == "full"
    # The client cannot choose the status.
    sent_full = {**PERSONA, "limits": ["L1", "L2"], "status": "full"}
    assert client.post("/studio/personas", json=sent_full).json()["status"] == "preview"
    pointer = {**PERSONA, "tool_groups": ["keyboard", "pointer", "navigation", "control"]}
    assert client.post("/studio/personas", json=pointer).json()["status"] == "preview"
    magnified = {
        **PERSONA,
        "character": "iris",
        "limits": ["L3"],
        "perception": "magnified",
        "magnification": 4,
        "tool_groups": ["pointer", "keyboard", "magnifier", "navigation", "control"],
    }
    assert client.post("/studio/personas", json=magnified).json()["status"] == "preview"


def test_persona_validation_errors(client):
    unknown_limit = client.post("/studio/personas", json={**PERSONA, "limits": ["L9"]})
    assert unknown_limit.status_code == 422
    assert unknown_limit.json()["detail"][0]["loc"] == ["body", "limits", 0]

    no_name = client.post("/studio/personas", json={**PERSONA, "name": "  "})
    assert no_name.status_code == 422 and "name" in message(no_name).lower()

    bad_character = client.post("/studio/personas", json={**PERSONA, "character": "dragon"})
    assert bad_character.status_code == 422
    assert bad_character.json()["detail"][0]["loc"] == ["body", "character"]

    no_tools = client.post("/studio/personas", json={**PERSONA, "tool_groups": []})
    assert no_tools.status_code == 422

    no_zoom = client.post("/studio/personas", json={**PERSONA, "perception": "magnified"})
    assert no_zoom.status_code == 422 and "magnification" in message(no_zoom)
    assert client.get("/studio/personas").json() == []


def test_built_in_items_are_read_only(client):
    for path in (
        "/studio/personas/keyboard-only",
        "/studio/sites/tallowmere",
        "/studio/tasks/buy-one",
    ):
        changed = client.put(path, json={})
        assert changed.status_code == 409
        assert "copy it first" in changed.json()["detail"]
        assert client.delete(path).status_code == 409
        # They can still be read, for example to duplicate them.
        assert client.get(path).status_code == 200


def test_a_copy_of_a_built_in_persona_is_a_new_custom_persona(client):
    knock = client.get("/studio/personas/keyboard-only").json()
    copy = client.post("/studio/personas", json={**knock, "name": "Knock (copy)"}).json()
    assert copy["id"] != "keyboard-only" and copy["id"].startswith("custom-")
    assert catalog.persona("keyboard-only").name == "Knock"


# ---------------------------------------------------------------- sites and tasks


def test_create_edit_list_and_delete_a_site(client):
    site = make_site(client)
    assert site["id"].startswith("custom-corner-shop-")
    assert site["origin"] == "http://localhost:3999"
    assert "honeytokens" not in site and "docker_host" not in site
    assert [s["id"] for s in client.get("/studio/sites").json()] == [site["id"]]
    assert site["id"] in {s["id"] for s in client.get("/sites").json()}
    assert "http://localhost:3999" in catalog.site_origins()

    edited = client.put(f"/studio/sites/{site['id']}", json={**SITE, "name": "Corner shop (new)"})
    assert edited.status_code == 200 and edited.json()["name"] == "Corner shop (new)"

    assert client.delete(f"/studio/sites/{site['id']}").status_code == 204
    assert client.get("/studio/sites").json() == []
    assert "http://localhost:3999" not in catalog.site_origins()


@pytest.mark.parametrize(
    "origin",
    [
        "localhost:3999",
        "ftp://example.com",
        "https://",
        "javascript:alert(1)",
        "https://a.com/shop",
    ],
)
def test_a_site_needs_an_http_origin_with_a_host(client, origin):
    response = client.post("/studio/sites", json={**SITE, "origin": origin})
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "origin"]


def test_create_edit_list_and_delete_a_task(client):
    site = make_site(client)
    task = make_task(client, site["id"])
    assert task["id"].startswith("custom-buy-one-dusk-ember-candle-")
    assert task["id"] in catalog.tasks()
    assert [t["id"] for t in client.get(f"/studio/tasks?site_id={site['id']}").json()] == [
        task["id"]
    ]
    assert task["id"] in {t["id"] for t in client.get(f"/sites/{site['id']}/tasks").json()}

    edited = client.put(
        f"/studio/tasks/{task['id']}",
        json={**task, "success": {"text_present": "Thank you", "answer_contains": [" ", "order"]}},
    )
    assert edited.status_code == 200
    assert edited.json()["success"]["text_present"] == "Thank you"
    assert edited.json()["success"]["answer_contains"] == ["order"]

    assert client.delete(f"/studio/tasks/{task['id']}").status_code == 204
    assert client.get("/studio/tasks").json() == []


def test_a_custom_task_may_use_a_built_in_site(client):
    task = make_task(client, "tallowmere")
    assert catalog.task(task["id"]).site_id == "tallowmere"


def test_task_validation_errors(client):
    site = make_site(client)
    unknown = client.post(
        "/studio/tasks",
        json={"site_id": "nowhere", "instruction": "x", "success": {"url_prefix": "/"}},
    )
    assert unknown.status_code == 422 and "no site" in message(unknown)

    unchecked = client.post(
        "/studio/tasks", json={"site_id": site["id"], "instruction": "x", "success": {}}
    )
    assert unchecked.status_code == 422 and "success check" in message(unchecked)

    bad_path = client.post(
        "/studio/tasks",
        json={
            "site_id": site["id"],
            "instruction": "x",
            "start_path": "shop",
            "success": {"url_prefix": "/"},
        },
    )
    assert bad_path.status_code == 422 and bad_path.json()["detail"][0]["loc"] == [
        "body",
        "start_path",
    ]

    bad_scenario = client.post(
        "/studio/tasks",
        json={
            "site_id": site["id"],
            "instruction": "x",
            "scenario": "dance",
            "success": {"url_prefix": "/"},
        },
    )
    assert bad_scenario.status_code == 422
    assert client.get("/studio/tasks").json() == []


def test_deleting_a_site_deletes_its_tasks(client):
    site = make_site(client)
    other = make_site(client, name="Other shop", origin="http://localhost:3998")
    make_task(client, site["id"])
    kept = make_task(client, other["id"])
    client.delete(f"/studio/sites/{site['id']}")
    assert [t["id"] for t in client.get("/studio/tasks").json()] == [kept["id"]]
    catalog.tasks()  # no task is left on an unknown site


def test_a_custom_task_on_a_custom_site_runs_with_the_fake_provider(client):
    persona = client.post("/studio/personas", json=PERSONA).json()
    site = make_site(client)
    task = make_task(client, site["id"])
    body = {
        "site_id": site["id"],
        "task_id": task["id"],
        "persona_id": persona["id"],
        "enforcement": ["gate"],
        "provider": "fake",
    }
    created = client.post("/runs", json=body)
    assert created.status_code == 202, created.text
    run_id = created.json()["id"]
    # TestClient runs background tasks before returning, so the run is finished here.
    summary = client.get(f"/runs/{run_id}").json()
    assert summary["status"] == "finished"
    assert summary["config"]["persona_id"] == persona["id"]
    assert client.get(f"/runs/{run_id}/steps").json()


def test_no_custom_items_without_the_api_store(monkeypatch):
    from vanguard.studio import source

    monkeypatch.setattr(deps, "_store", None)
    assert source.personas() == {} and source.sites() == {} and source.tasks() == {}
