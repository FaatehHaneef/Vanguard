import json

from PIL import Image
from test_agent_loop import KEYS, run  # noqa: F401

from vanguard import bundle, labels
from vanguard.contracts import Action, EnforcementOption
from vanguard.settings import Settings
from vanguard.store import RunStore

click = Action(tool="click", ref="e0", rationale="shortcut")


def make_store(path):
    store = RunStore(f"sqlite:///{path}")
    store.create_schema()
    return store


def test_round_trip(tmp_path):
    source = make_store(tmp_path / "source.db")
    for option in (EnforcementOption.PROMPT_ONLY, EnforcementOption.GATE):
        summary = run(source, "keyboard-only", [option], [click, *KEYS])
        # Give every run's first step a screenshot, as the real executor would.
        shot = tmp_path / f"{summary.id}.png"
        Image.new("RGB", (1280, 720), "white").save(shot)
        with source._session() as session, session.begin():
            from vanguard.store import RunRow, StepRow

            row = session.get(StepRow, (summary.id, 0))
            record = dict(row.record)
            record["observation"] = {**record["observation"], "screenshot_path": str(shot)}
            row.record = record
            session.get(RunRow, summary.id).batch_id = "b1"

    out = tmp_path / "bundle"
    result = bundle.export_bundle(source, ["b1"], out, "t", count=5)
    assert result["items"] == 5
    data = json.loads((out / "bundle.json").read_text())
    assert "attempted" not in json.dumps(data)  # blind: no checker verdicts
    shots = list((out / "shots").glob("*.jpg"))
    assert all(Image.open(p).width == 960 for p in shots)

    # Two labellers import the same bundle and see the same steps in the same order.
    settings = Settings(data_dir=tmp_path / "data")
    orders = []
    for name in ("alice", "bob"):
        mine = make_store(tmp_path / f"{name}.db")
        assert bundle.import_bundle(mine, out, settings)["batch_id"] == "label-t"
        items = labels.next_items(mine, name, 10, "label-t")
        orders.append([(i.run_id, i.index) for i in items])
        for item in items:
            labels.save_label(
                mine,
                labels.Label(run_id=item.run_id, index=item.index, labeller=name, verdict="no"),
            )
        assert bundle.export_labels(mine, name, tmp_path / "labels" / f"{name}.json") == 5
    assert orders[0] == orders[1] == [(i["run_id"], i["index"]) for i in data["items"]]

    # Back on the source machine: import both files and compute agreement.
    files = [tmp_path / "labels" / "alice.json", tmp_path / "labels" / "bob.json"]
    assert bundle.import_labels(source, files) == 10
    report = labels.agreement(source, "alice", "bob")
    assert report["overlap"] == 5 and report["raw_agreement"] == 1.0
