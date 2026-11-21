from test_api import client  # noqa: F401  (fixture)


def _runs(client, n=2):  # noqa: F811
    for option in (["prompt_only"], ["gate"])[:n]:
        body = {
            "site_id": "tallowmere",
            "task_id": "buy-one",
            "persona_id": "keyboard-only",
            "enforcement": option,
            "provider": "fake",
        }
        client.post("/runs", json=body)


def test_items_are_blind_and_shared(client):  # noqa: F811
    _runs(client)
    alice = client.get("/labelling/next", params={"labeller": "alice", "count": 5}).json()
    bob = client.get("/labelling/next", params={"labeller": "bob", "count": 5}).json()
    assert [(i["run_id"], i["index"]) for i in alice] == [(i["run_id"], i["index"]) for i in bob]
    assert "attempted" not in str(alice[0]) and "executed_leak" not in str(alice[0])


def test_labels_and_agreement(client):  # noqa: F811
    _runs(client)
    items = client.get("/labelling/next", params={"labeller": "alice", "count": 6}).json()
    for n, item in enumerate(items):
        key = {"run_id": item["run_id"], "index": item["index"]}
        client.post("/labels", json={**key, "labeller": "alice", "verdict": "no"})
        verdict = "yes" if n == 0 else "no"
        extra = {"limit": "L1", "kind": "action"} if verdict == "yes" else {}
        client.post("/labels", json={**key, "labeller": "bob", "verdict": verdict, **extra})
    # Labelled items are not offered again.
    again = client.get("/labelling/next", params={"labeller": "alice", "count": 6}).json()
    assert not {(i["run_id"], i["index"]) for i in again} & {
        (i["run_id"], i["index"]) for i in items
    }
    report = client.get("/labelling/agreement", params={"first": "alice", "second": "bob"}).json()
    assert report["overlap"] == len(items)
    assert report["raw_agreement"] == (len(items) - 1) / len(items)
    assert len(report["disagreements"]) == 1
    assert "checker_vs_alice" in report and "checker_vs_agreed" in report
    people = client.get("/labelling/labellers").json()
    assert people == [
        {"labeller": "alice", "labels": len(items)},
        {"labeller": "bob", "labels": len(items)},
    ]


def test_yes_needs_a_limit(client):  # noqa: F811
    _runs(client, 1)
    item = client.get("/labelling/next", params={"labeller": "a"}).json()[0]
    body = {"run_id": item["run_id"], "index": item["index"], "labeller": "a", "verdict": "yes"}
    assert client.post("/labels", json=body).status_code == 422
    body["index"] = 999
    assert client.post("/labels", json=body).status_code == 404
