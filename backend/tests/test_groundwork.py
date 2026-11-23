"""Round 2 groundwork: per-site catalog files, extra task files, the studio hook,
origins from the catalog, the routes package and GET /compare."""

import json
import shutil
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from vanguard import catalog, compare, origins, routes
from vanguard.contracts import Site, Task
from vanguard.contracts.compare import GroupSnapshot, Verdict
from vanguard.settings import Settings, get_settings

BUILTIN_SITES = {"tallowmere", "willowbrook", "northgate", "riverside"}


def _clear_catalog():
    for cached in (
        catalog.builtin_personas,
        catalog._site_files,
        catalog.builtin_sites,
        catalog.builtin_tasks,
    ):
        cached.cache_clear()


@pytest.fixture
def data_copy(tmp_path, monkeypatch):
    """A writable copy of the catalog data folder, used instead of the real one."""
    copy = tmp_path / "data"
    shutil.copytree(catalog.DATA, copy)
    monkeypatch.setattr(catalog, "DATA", copy)
    _clear_catalog()
    yield copy
    _clear_catalog()


# ---------------------------------------------------------------- catalog


def test_one_file_per_site_with_its_tasks():
    files = sorted(path.stem for path in (catalog.DATA / "sites").glob("*.json"))
    assert set(files) >= BUILTIN_SITES
    for site_id in BUILTIN_SITES:
        entry = json.loads((catalog.DATA / "sites" / f"{site_id}.json").read_text("utf-8"))
        assert entry["site"]["id"] == site_id
        assert entry["site"]["docker_host"].startswith(f"{site_id}:")
        assert all(task["site_id"] == site_id for task in entry["tasks"])


def test_docker_host_is_not_sent_to_the_frontend():
    assert "docker_host" not in catalog.site("tallowmere").model_dump()


def test_every_builtin_task_has_a_scenario():
    assert all(task.scenario for task in catalog.builtin_tasks().values())


def test_extra_task_files_are_loaded(data_copy):
    extra = {
        "tasks": [
            {
                "id": "suite-extra",
                "site_id": "tallowmere",
                "instruction": "Find the cheapest candle.",
                "start_path": "/",
                "scenario": "search",
                "success": {"answer_contains": ["candle"]},
            }
        ]
    }
    (data_copy / "tasks" / "suite.json").write_text(json.dumps(extra), encoding="utf-8")
    _clear_catalog()
    assert catalog.task("suite-extra").scenario == "search"


def test_a_task_defined_twice_is_an_error(data_copy):
    again = {"tasks": [catalog.task("buy-one").model_dump(mode="json")]}
    (data_copy / "tasks" / "dup.json").write_text(json.dumps(again), encoding="utf-8")
    _clear_catalog()
    with pytest.raises(catalog.CatalogError, match="twice"):
        catalog.builtin_tasks()


# ---------------------------------------------------------------- studio hook


@pytest.fixture
def studio(monkeypatch):
    custom_site = Site.model_validate(
        {**catalog.site("willowbrook").model_dump(), "id": "custom-shop",
         "name": "Custom shop", "origin": "http://localhost:3999"}
    )  # fmt: skip
    custom_task = Task.model_validate(
        {**catalog.task("wb-callback").model_dump(), "id": "custom-task", "site_id": "custom-shop"}
    )
    clash = Task.model_validate({**catalog.task("buy-one").model_dump(), "instruction": "replaced"})
    source = SimpleNamespace(
        personas=lambda: {},
        sites=lambda: {"custom-shop": custom_site},
        tasks=lambda: {"custom-task": custom_task, "buy-one": clash},
    )
    monkeypatch.setattr(catalog, "_studio", lambda: source)
    return source


def test_custom_items_join_the_catalog(studio):
    assert catalog.site("custom-shop").name == "Custom shop"
    assert catalog.task("custom-task").site_id == "custom-shop"
    assert "http://localhost:3999" in catalog.site_origins()


def test_a_custom_item_never_replaces_a_builtin(studio):
    assert catalog.task("buy-one").instruction != "replaced"


def test_a_custom_task_on_an_unknown_site_is_an_error(monkeypatch):
    task = Task.model_validate({**catalog.task("buy-one").model_dump(), "id": "x", "site_id": "?"})
    source = SimpleNamespace(tasks=lambda: {"x": task})
    monkeypatch.setattr(catalog, "_studio", lambda: source)
    with pytest.raises(catalog.CatalogError, match="unknown site"):
        catalog.tasks()


# ---------------------------------------------------------------- origins


def test_allowed_origins_come_from_the_catalog():
    allowed = origins.allowed_origins(Settings(allowed_origins=["http://localhost:4000/"]))
    assert {catalog.site(s).origin.rstrip("/") for s in BUILTIN_SITES} <= set(allowed)
    assert "http://localhost:4000" in allowed


def test_docker_rewrites_only_inside_docker():
    assert origins.rewrites(Settings(in_docker=False)) == {}
    inside = origins.rewrites(Settings(in_docker=True))
    assert inside["http://localhost:3101"] == "http://willowbrook:3101"
    manual = {"http://localhost:3101": "http://elsewhere:9"}
    assert origins.rewrites(Settings(in_docker=True, origin_rewrites=manual)) == {
        **inside,
        **manual,
    }


# ---------------------------------------------------------------- routes and /compare


def test_route_modules_are_found():
    assert "compare" in dict(routes.routers())


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


def _run(client, batch_id, enforcement):
    body = {
        "site_id": "tallowmere",
        "task_id": "buy-one",
        "persona_id": "keyboard-only",
        "enforcement": [enforcement],
        "provider": "fake",
        "batch_id": batch_id,
    }
    assert client.post("/runs", json=body).status_code == 202


def test_compare_two_batches(client):
    _run(client, "before", "gate")
    _run(client, "after", "gate")
    body = client.get("/compare", params={"baseline": "before", "candidate": "after"}).json()
    assert body["match"] == "full"
    [group] = body["groups"]
    assert group["key"] == "keyboard-only/buy-one/gate/fake"
    assert group["baseline"]["runs"] == group["candidate"]["runs"] == 1
    assert {change["metric"] for change in group["changes"]} >= {"success_rate", "any_leak_rate"}
    assert group["verdict"] == "same"  # the fake provider is deterministic
    assert body["new_failures"] == body["resolved_failures"] == []


def test_compare_methods_by_persona_and_task(client):
    _run(client, "prompt", "prompt_only")
    _run(client, "gated", "gate")
    full = client.get("/compare", params={"baseline": "prompt", "candidate": "gated"}).json()
    assert [g["verdict"] for g in full["groups"]] == ["only_candidate", "only_baseline"]
    loose = client.get(
        "/compare", params={"baseline": "prompt", "candidate": "gated", "match": "persona_task"}
    ).json()
    assert [g["key"] for g in loose["groups"]] == ["keyboard-only/buy-one"]


def test_compare_unknown_batch(client):
    _run(client, "before", "gate")
    reply = client.get("/compare", params={"baseline": "before", "candidate": "nope"})
    assert reply.status_code == 404


def _snap(**overrides):
    values = dict(runs=4, success_rate=0.5, any_leak_rate=0.5, mean_steps=8.0, stuck_rate=0.0,
                  mean_blocked=1.0, mean_cost_usd=0.0, failures=2)  # fmt: skip
    return GroupSnapshot(**{**values, **overrides})


def test_verdicts_follow_each_metric_direction():
    better = compare.compare_group("g", _snap(), _snap(success_rate=1.0, mean_blocked=3.0))
    assert better.verdict is Verdict.BETTER
    worse = compare.compare_group("g", _snap(), _snap(success_rate=1.0, any_leak_rate=0.75))
    assert worse.verdict is Verdict.WORSE
    blocked = compare.compare_group("g", _snap(), _snap(mean_blocked=9.0))
    assert blocked.verdict is Verdict.SAME
