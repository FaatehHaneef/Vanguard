"""Labelling bundles: move a fixed labelling sample between machines through git.

The person who ran the batches exports a bundle; each labeller imports it, labels on
/labelling, and exports their labels to a JSON file committed on their own branch; the
labels are then imported back for the agreement report.

    python -m vanguard.cli labelling export --batches a3-tallowmere a3-willowbrook \\
        --name a3 --count 60                         # writes data/labelling/a3/
    python -m vanguard.cli labelling import data/labelling/a3
    python -m vanguard.cli labelling export-labels --labeller hadi   # data/labels/hadi.json
    python -m vanguard.cli labelling import-labels data/labels/*.json

A bundle holds only the sampled steps, their run summaries and one small JPEG per step,
never the checker's verdicts, so labelling stays blind. The sample order is fixed in the
bundle, so every labeller sees the same steps in the same order.
"""

import json
import random
import shutil
from pathlib import Path

from sqlalchemy import delete

from vanguard import catalog, labels
from vanguard.contracts import PersonaStatus, RunStatus, StepRecord
from vanguard.labels import SampleRow
from vanguard.settings import Settings
from vanguard.store import RunRow, RunStore, StepRow, _now

BUNDLE_FILE = "bundle.json"
SAMPLE_SEED = 4009
SHOT_WIDTH = 960
SHOT_QUALITY = 70


def _shrink(source: Path, target: Path) -> None:
    from PIL import Image  # only the exporting side needs Pillow

    with Image.open(source) as image:
        image = image.convert("RGB")
        if image.width > SHOT_WIDTH:
            height = round(image.height * SHOT_WIDTH / image.width)
            image = image.resize((SHOT_WIDTH, height))
        image.save(target, "JPEG", quality=SHOT_QUALITY, optimize=True)


def export_bundle(
    store: RunStore, batches: list[str], out: Path, name: str, count: int = 60
) -> dict:
    """Sample `count` steps from finished runs of full (evaluated) personas."""
    keys = []
    summaries = {}
    for batch_id in batches:
        for run in store.list_runs(batch_id, limit=100_000):
            persona = catalog.persona(run.config.persona_id)
            if run.status is not RunStatus.FINISHED or persona.status is not PersonaStatus.FULL:
                continue
            summaries[run.id] = run
            keys.extend((run.id, index) for index in range(run.steps))
    keys.sort()
    random.Random(SAMPLE_SEED).shuffle(keys)
    chosen = keys[:count]

    out.mkdir(parents=True, exist_ok=True)
    shots = out / "shots"
    shots.mkdir(exist_ok=True)
    steps_by_run: dict[str, dict[int, StepRecord]] = {}
    items = []
    for run_id, index in chosen:
        if run_id not in steps_by_run:
            steps_by_run[run_id] = {s.index: s for s in store.steps(run_id)}
        step = steps_by_run[run_id][index]
        shot = None
        if step.observation.screenshot_path and Path(step.observation.screenshot_path).is_file():
            shot = f"shots/{run_id[:12]}-{index:03d}.jpg"
            _shrink(Path(step.observation.screenshot_path), out / shot)
        record = step.model_dump(mode="json")
        record["observation"]["screenshot_path"] = None
        items.append({"run_id": run_id, "index": index, "shot": shot, "step": record})

    runs = {
        run_id: summaries[run_id].model_dump(mode="json")
        for run_id in dict.fromkeys(run_id for run_id, _ in chosen)
    }
    bundle = {"name": name, "batches": batches, "seed": SAMPLE_SEED, "runs": runs, "items": items}
    (out / BUNDLE_FILE).write_text(json.dumps(bundle, indent=1), encoding="utf-8")
    return {"name": name, "items": len(items), "runs": len(runs)}


def import_bundle(store: RunStore, folder: Path, settings: Settings) -> dict:
    """Load a bundle into the local store under the batch id `label-<name>`."""
    bundle = json.loads((folder / BUNDLE_FILE).read_text(encoding="utf-8"))
    name = bundle["name"]
    batch_id = f"label-{name}"
    shots_dir = Path(settings.data_dir) / "screenshots" / batch_id
    shots_dir.mkdir(parents=True, exist_ok=True)
    with store._session() as session, session.begin():
        session.execute(delete(SampleRow).where(SampleRow.sample == batch_id))
        for run_id, summary in bundle["runs"].items():
            row = session.get(RunRow, run_id)
            if row is None:
                config = {**summary["config"], "batch_id": batch_id}
                session.add(
                    RunRow(
                        id=run_id,
                        batch_id=batch_id,
                        label=summary["id"],
                        config=config,
                        status=summary["status"],
                        outcome=summary["outcome"],
                        steps=summary["steps"],
                        blocked=summary["blocked"],
                        created_at=_now(),
                        finished_at=_now(),
                        error=summary.get("error"),
                    )
                )
        session.flush()
        for position, item in enumerate(bundle["items"]):
            record = item["step"]
            if item["shot"]:
                target = shots_dir / Path(item["shot"]).name
                shutil.copyfile(folder / item["shot"], target)
                record["observation"]["screenshot_path"] = str(target)
            existing = session.get(StepRow, (item["run_id"], item["index"]))
            if existing is None:
                session.add(StepRow(run_id=item["run_id"], index=item["index"], record=record))
            session.add(
                SampleRow(
                    sample=batch_id, position=position, run_id=item["run_id"], index=item["index"]
                )
            )
    return {"batch_id": batch_id, "items": len(bundle["items"])}


def export_labels(store: RunStore, labeller: str, out: Path) -> int:
    found = labels.labels(store, labeller)
    out.parent.mkdir(parents=True, exist_ok=True)
    data = [
        label.model_dump(mode="json") for label in sorted(found, key=lambda x: (x.run_id, x.index))
    ]
    out.write_text(json.dumps({"labeller": labeller, "labels": data}, indent=1), encoding="utf-8")
    return len(data)


def import_labels(store: RunStore, files: list[Path]) -> int:
    count = 0
    for file in files:
        payload = json.loads(file.read_text(encoding="utf-8"))
        for item in payload["labels"]:
            labels.save_label(store, labels.Label.model_validate(item))
            count += 1
    return count
