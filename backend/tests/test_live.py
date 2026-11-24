"""Live view: frame files and the MJPEG stream (vanguard.live, routes/live.py)."""

import asyncio

import pytest
from fastapi.testclient import TestClient

from vanguard import live
from vanguard.routes import live as live_route
from vanguard.settings import Settings, get_settings

JPEG = b"\xff\xd8 fake frame \xff\xd9"


def test_frames_are_replaced_whole_and_cleared(tmp_path):
    path = live.frame_path(Settings(data_dir=tmp_path), "run/../x1")
    assert (
        path.parent == tmp_path / "live" and path.name == "runx1.jpg"
    )  # no path separators survive
    live.write_frame(path, JPEG)
    live.write_frame(path, JPEG + b"2")
    assert live.read_frame(path) == JPEG + b"2"
    assert not path.with_suffix(".tmp").exists()
    live.clear(path)
    assert live.read_frame(path) is None


class FakeRequest:
    async def is_disconnected(self):
        return False


class FakeStore:
    def __init__(self, polls_running):
        self.left = polls_running

    def get_run(self, run_id):
        from types import SimpleNamespace

        from vanguard.contracts import RunStatus

        self.left -= 1
        return SimpleNamespace(status=RunStatus.RUNNING if self.left > 0 else RunStatus.FINISHED)


def test_the_stream_sends_each_frame_once_and_ends_with_the_run(tmp_path):
    path = tmp_path / "f.jpg"
    live.write_frame(path, JPEG)

    async def collect():
        parts = []
        async for part in live_route.frames(FakeRequest(), FakeStore(2), "r", path, poll=0.001):
            parts.append(part)
        return parts

    parts = asyncio.run(collect())
    assert parts[0] == b"--frame\r\n" and len(parts) == 2
    assert parts[1].startswith(b"Content-Type: image/jpeg") and JPEG in parts[1]
    assert parts[1].endswith(b"\r\n--frame\r\n")  # closed at once, so it shows at once


@pytest.fixture
def client(monkeypatch, tmp_path):
    monkeypatch.setenv("VANGUARD_DATABASE_URL", f"sqlite:///{tmp_path / 'test.db'}")
    monkeypatch.setenv("VANGUARD_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("VANGUARD_EXECUTOR", "fake")
    monkeypatch.setenv("VANGUARD_ENABLED_PROVIDERS", '["fake"]')
    get_settings.cache_clear()
    from vanguard.api import app

    with TestClient(app) as client:
        yield client
    get_settings.cache_clear()


def test_live_endpoints(client, tmp_path):
    body = {"site_id": "tallowmere", "task_id": "buy-one", "persona_id": "keyboard-only",
            "provider": "fake"}  # fmt: skip
    run_id = client.post("/runs", json=body).json()["id"]
    # The run has finished (TestClient runs background tasks first), so there is no stream.
    assert client.get(f"/runs/{run_id}/live").status_code == 409
    assert client.get("/runs/nope/live").status_code == 404
    assert client.get(f"/runs/{run_id}/live/frame").status_code == 404
    live.write_frame(live.frame_path(get_settings(), run_id), JPEG)
    frame = client.get(f"/runs/{run_id}/live/frame")
    assert frame.status_code == 200 and frame.content == JPEG
