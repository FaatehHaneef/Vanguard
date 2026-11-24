"""Live view of a running test browser (vanguard.live).

GET /runs/{id}/live/frame  the latest frame as one JPEG, or 404 when there is none.
                           The run page fetches it several times a second.
GET /runs/{id}/live        the same frames as an MJPEG stream (multipart/x-mixed-replace)
                           for other viewers; it ends when the run ends.
"""

import asyncio
from collections.abc import AsyncIterator

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import Response, StreamingResponse

from vanguard import live
from vanguard.contracts import RunStatus
from vanguard.deps import get_settings, get_store
from vanguard.settings import Settings
from vanguard.store import RunStore

router = APIRouter(tags=["live"])

BOUNDARY = "frame"
POLL_SECONDS = 0.1
STATUS_EVERY = 10  # polls between checks of the run's status
NO_CACHE = {"Cache-Control": "no-store"}


def _active(store: RunStore, run_id: str) -> bool:
    run = store.get_run(run_id)
    return run is not None and run.status in (RunStatus.QUEUED, RunStatus.RUNNING)


OPEN = f"--{BOUNDARY}\r\n".encode()


def _part(data: bytes) -> bytes:
    """One frame, closed by the next boundary at once: browsers show a part only when
    the boundary after it arrives, and the next frame may be a long time coming."""
    head = f"Content-Type: image/jpeg\r\nContent-Length: {len(data)}\r\n\r\n"
    return head.encode() + data + b"\r\n" + OPEN


async def frames(
    request: Request, store: RunStore, run_id: str, path, poll: float = POLL_SECONDS
) -> AsyncIterator[bytes]:
    """Each new frame once, until the run ends or the viewer goes away."""
    last = None
    polls = 0
    yield OPEN
    while True:
        try:
            stamp = path.stat().st_mtime_ns
        except OSError:
            stamp = None
        if stamp is not None and stamp != last:
            data = live.read_frame(path)
            if data:
                last = stamp
                yield _part(data)
        polls += 1
        if polls % STATUS_EVERY == 0:
            if await request.is_disconnected() or not _active(store, run_id):
                return
        await asyncio.sleep(poll)


@router.get("/runs/{run_id}/live")
async def live_stream(
    run_id: str,
    request: Request,
    settings: Settings = Depends(get_settings),
    store: RunStore = Depends(get_store),
) -> StreamingResponse:
    """The browser's screen while the run goes, characters included."""
    if store.get_run(run_id) is None:
        raise HTTPException(404, "run not found")
    if not _active(store, run_id):
        raise HTTPException(409, "the run is not running; see its step screenshots")
    return StreamingResponse(
        frames(request, store, run_id, live.frame_path(settings, run_id)),
        media_type=f"multipart/x-mixed-replace; boundary={BOUNDARY}",
        headers=NO_CACHE,
    )


@router.get("/runs/{run_id}/live/frame")
def live_frame(run_id: str, settings: Settings = Depends(get_settings)) -> Response:
    data = live.read_frame(live.frame_path(settings, run_id))
    if data is None:
        raise HTTPException(404, "no live frame")
    return Response(data, media_type="image/jpeg", headers=NO_CACHE)
