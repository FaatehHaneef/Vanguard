"""Live view: the test browser's screen while a run is going, for the run page.

The Playwright executor asks Chromium for a screencast (CDP Page.startScreencast) and
writes each frame to data_dir/live/<run_id>.jpg. The run page fetches the latest
frame several times a second (GET /runs/{id}/live/frame); GET /runs/{id}/live streams
the same frames as MJPEG for other viewers. A file rather than memory, so runs started
from the command line (batches) can be watched in the web app too. The HUD overlay is
part of the page, so the characters appear in the picture.

The file is removed when the run ends; the saved step screenshots are the record.
"""

import contextlib
import os
from pathlib import Path

from vanguard.settings import Settings

FRAME_QUALITY = 60
MAX_WIDTH = 1280
MAX_HEIGHT = 900


def frame_path(settings: Settings, run_id: str) -> Path:
    safe = "".join(ch for ch in run_id if ch.isalnum() or ch in "-_")
    return Path(settings.data_dir) / "live" / f"{safe}.jpg"


def write_frame(path: Path, data: bytes) -> None:
    """Replace the frame atomically, so a reader never sees half a picture. A frame
    that cannot be written (the reader holds the file on Windows) is skipped."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(".tmp")
    try:
        temp.write_bytes(data)
        os.replace(temp, path)
    except OSError:
        with contextlib.suppress(OSError):
            temp.unlink()


def read_frame(path: Path) -> bytes | None:
    try:
        return path.read_bytes()
    except OSError:
        return None


def clear(path: Path) -> None:
    for leftover in (path, path.with_suffix(".tmp")):
        with contextlib.suppress(OSError):
            leftover.unlink()
