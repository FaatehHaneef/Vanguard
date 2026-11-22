"""PlaywrightExecutor against a small local page. Skipped when Chromium is not installed."""

import asyncio
import functools
import http.server
import threading
from datetime import UTC, datetime
from pathlib import Path

import pytest

playwright = pytest.importorskip("playwright.async_api")

from vanguard.contracts import Action, Site, Task, Tool  # noqa: E402
from vanguard.contracts.sites import SuccessCheck  # noqa: E402
from vanguard.executor.playwright import PlaywrightExecutor  # noqa: E402
from vanguard.settings import Settings  # noqa: E402

PAGE = """<!doctype html>
<html><head><title>Fixture shop</title>
<style>
  button:focus { outline: 3px solid #1b1f3b; }
  .plain:focus { outline: none; }
  .box { cursor: pointer; display: inline-block; width: 16px; }
</style></head>
<body>
  <h1>Fixture shop</h1>
  <p>Dusk Ember <b>$18.00</b></p>
  <button id="shown">Shown focus</button>
  <button class="plain" id="hidden">Add to cart</button>
  <div class="box" onclick="document.title='plus'">+</div>
  <a href="/next.html">Next page</a>
  <img src="http://blocked.invalid/pixel.png" alt="">
  <p style="margin-top: 1500px">Far away text</p>
</body></html>"""

NEXT = "<!doctype html><title>Next</title><h1>Thanks</h1>"

# Sites often give <main> tabindex="-1" so focus can move there after navigation; that
# must not turn the whole page into one control.
WRAPPED = """<!doctype html><title>Wrapped</title>
<main id="main" tabindex="-1"><h1 tabindex="-1">Results</h1>
<a href="/next.html">First result</a><button>Filter</button></main>"""


@pytest.fixture(scope="module")
def site(tmp_path_factory):
    root: Path = tmp_path_factory.mktemp("site")
    (root / "index.html").write_text(PAGE)
    (root / "next.html").write_text(NEXT)
    (root / "wrapped.html").write_text(WRAPPED)
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(root))
    handler.log_message = lambda *args: None
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    origin = f"http://127.0.0.1:{server.server_address[1]}"
    yield Site(id="fixture", name="Fixture", origin=origin)
    server.shutdown()


def _task() -> Task:
    return Task(id="t", site_id="fixture", instruction="x", success=SuccessCheck(url_prefix="/x"))


def _run(site, body):
    async def main():
        settings = Settings(allowed_origins=[site.origin], screenshots=False)
        executor = PlaywrightExecutor(settings)
        try:
            await executor.start(site, _task(), persona=None)
        except Exception as error:  # Chromium not installed
            await executor.close()
            pytest.skip(f"browser unavailable: {error}")
        try:
            return await body(executor)
        finally:
            await executor.close()

    return asyncio.run(main())


def _ref(content: str, label: str) -> str:
    line = next(line for line in content.splitlines() if label in line and line.startswith("["))
    return line[1 : line.index("]")]


def test_observation_lists_elements_text_and_links(site):
    async def body(ex):
        obs = await ex.observe()
        assert "# Fixture shop" in obs.content
        assert "Dusk Ember $18.00" in obs.content
        assert 'button "Add to cart"' in obs.content
        assert 'clickable "+"' in obs.content
        assert 'link "Next page" -> /next.html' in obs.content
        assert obs.links == [site.origin + "/next.html"]
        assert any("blocked.invalid" in url for url in ex.blocked)

    _run(site, body)


def test_focus_reported_only_when_visible(site):
    async def body(ex):
        result = await ex.execute(Action(tool=Tool.PRESS, key="Tab"))
        obs = await ex.observe()
        shown = _ref(obs.content, "Shown focus")
        assert result.focus_after == shown
        assert f"Keyboard focus: {shown}" in obs.content
        assert any(e.type == "keydown" and e.trusted and e.target == "Tab" for e in result.events)
        assert any(e.type == "focusin" for e in result.events)

        result = await ex.execute(Action(tool=Tool.PRESS, key="Tab"))
        obs = await ex.observe()
        assert result.focus_after == _ref(obs.content, "Add to cart")
        assert "Keyboard focus" not in obs.content  # outline removed: focus is invisible

    _run(site, body)


def test_click_records_trusted_pointer_events_and_box(site):
    async def body(ex):
        obs = await ex.observe()
        plus = _ref(obs.content, 'clickable "+"')
        result = await ex.execute(Action(tool=Tool.CLICK, ref=plus))
        assert result.error is None
        assert result.target_box is not None and result.target_box.width > 0
        downs = [e for e in result.events if e.type in ("pointerdown", "mousedown")]
        assert downs and all(e.trusted for e in downs)
        assert downs[0].target == plus
        assert (await ex.observe()).content.startswith("Page title: plus")

    _run(site, body)


def test_navigation_and_missing_ref(site):
    async def body(ex):
        result = await ex.execute(Action(tool=Tool.CLICK, ref="e99"))
        assert result.error and "e99" in result.error
        obs = await ex.observe()
        result = await ex.execute(Action(tool=Tool.CLICK, ref=_ref(obs.content, "Next page")))
        assert result.url_after == site.origin + "/next.html"
        assert "Thanks" in await ex.page_text()
        result = await ex.execute(Action(tool=Tool.GOTO, url="/"))
        assert result.url_after == site.origin + "/"

    _run(site, body)


def test_hud_is_shown_but_never_observed_or_recorded(site):
    from vanguard import catalog

    knock = catalog.persona("keyboard-only")

    async def main():
        settings = Settings(allowed_origins=[site.origin], screenshots=False, hud=True)
        ex = PlaywrightExecutor(settings)
        try:
            await ex.start(site, _task(), knock)
        except Exception as error:
            await ex.close()
            pytest.skip(f"browser unavailable: {error}")
        try:
            result = await ex.execute(Action(tool=Tool.PRESS, key="Tab"))
            host = await ex.page.evaluate(
                "() => { const h = document.querySelector('[data-vanguard-hud]');"
                " return h && [h.getAttribute('aria-hidden'), h.hasAttribute('inert')]; }"
            )
            assert host == ["true", True]
            obs = await ex.observe()
            assert "Vanguard test" not in obs.content and "press" not in obs.content
            assert [e.type for e in result.events if e.trusted] == ["keydown", "focusin"]
            snapshot = await ex.page.locator("html").aria_snapshot()
            assert "Vanguard" not in snapshot
            await ex.announce(Action(tool=Tool.CLICK, ref="e3"), "Refused", "refused")
        finally:
            await ex.close()

    asyncio.run(main())


def test_conditions_mobile_and_slow_network(site):
    from vanguard.contracts import Condition

    async def main():
        settings = Settings(allowed_origins=[site.origin], screenshots=False, hud=False)
        ex = PlaywrightExecutor(settings, conditions=[Condition.MOBILE, Condition.SLOW_NETWORK])
        try:
            began = asyncio.get_running_loop().time()
            await ex.start(site, _task(), persona=None)
            load_seconds = asyncio.get_running_loop().time() - began
        except Exception as error:
            await ex.close()
            pytest.skip(f"browser unavailable: {error}")
        try:
            width = await ex.page.evaluate("() => screen.width")  # no viewport meta: layout is 980
            touch = await ex.page.evaluate("() => navigator.maxTouchPoints > 0")
            assert width == 390 and touch
            assert load_seconds > 0.4  # at least one 400 ms round trip
            obs = await ex.observe()
            plus = _ref(obs.content, 'clickable "+"')
            result = await ex.execute(Action(tool=Tool.CLICK, ref=plus))
            assert result.error is None
            assert any(e.type == "pointerdown" and e.trusted for e in result.events)
        finally:
            await ex.close()

    asyncio.run(main())


def test_screen_reader_perception_and_commands(site):
    from vanguard import catalog
    from vanguard.contracts import PerceptionMode

    echo = catalog.persona("screen-reader")

    async def main():
        settings = Settings(allowed_origins=[site.origin], screenshots=False, hud=True)
        ex = PlaywrightExecutor(settings, bounded_perception=True)
        try:
            await ex.start(site, _task(), echo)
        except Exception as error:
            await ex.close()
            pytest.skip(f"browser unavailable: {error}")
        try:
            obs = await ex.observe()
            assert obs.mode is PerceptionMode.ACCESSIBILITY_TREE
            assert 'heading level 1 "Fixture shop"' in obs.content
            assert 'button "Add to cart"' in obs.content
            assert "clickable" not in obs.content and "Vanguard test" not in obs.content
            assert obs.content.endswith("Screen reader cursor: top of the page")

            result = await ex.execute(Action(tool=Tool.SR_NEXT, kind="button"))
            assert result.error is None and result.target_box is not None
            assert [e.type for e in result.events if e.trusted] == ["focusin"]
            obs = await ex.observe()
            assert "Screen reader cursor: a" in obs.content and "Shown focus" in obs.content

            result = await ex.execute(Action(tool=Tool.SR_NEXT, kind="link"))
            result = await ex.execute(Action(tool=Tool.SR_ACTIVATE))
            assert any(e.type == "keydown" and e.trusted for e in result.events)
            assert result.url_after == site.origin + "/next.html"
            result = await ex.execute(Action(tool=Tool.SR_NEXT, kind="form_field"))
            assert result.error == "no form field after here"
        finally:
            await ex.close()

    asyncio.run(main())


def test_magnifier_window_and_pan(site):
    from vanguard import catalog
    from vanguard.checker import check_step
    from vanguard.contracts import GateDecision, PerceptionMode, StepRecord

    iris = catalog.persona("magnifier")

    async def main():
        settings = Settings(allowed_origins=[site.origin], screenshots=False, hud=False)
        ex = PlaywrightExecutor(settings, bounded_perception=True)
        try:
            await ex.start(site, _task(), iris)
        except Exception as error:
            await ex.close()
            pytest.skip(f"browser unavailable: {error}")
        try:
            # Panning works before the first observation too.
            await ex.execute(Action(tool=Tool.PAN, dx=0, dy=400))
            assert ex._window.y == 400
            await ex.execute(Action(tool=Tool.PAN, dx=0, dy=-400))
            obs = await ex.observe()
            assert obs.mode is PerceptionMode.MAGNIFIED
            assert obs.window.width == 320 and obs.window.height == 180
            assert "Magnified view at 400%" in obs.content and "# Fixture shop" in obs.content
            assert "Far away text" not in obs.content

            await ex.execute(Action(tool=Tool.PAN, dx=0, dy=1500))
            far = await ex.observe()
            assert "Far away text" in far.content and "# Fixture shop" not in far.content
            assert far.window.y > 1000

            # Clicking the heading's button from far away is outside the window: H3a.
            full = await ex._snapshot()
            ref = next(line[1 : line.index("]")] for line in full["lines"] if "Add to cart" in line)
            result = await ex.execute(Action(tool=Tool.CLICK, ref=ref))
            record = StepRecord(
                run_id="r",
                index=0,
                started_at=datetime.now(UTC),
                observation=far,
                proposed=Action(tool=Tool.CLICK, ref=ref),
                gate=GateDecision(allowed=True),
                executed=True,
                target_box=result.target_box,
            )
            verdict = check_step(record, iris, site.origin + "/")
            assert [v.rule for v in verdict.executed] == ["H3a"]

            await ex.execute(Action(tool=Tool.PRESS, key="Tab"))
            await ex.execute(Action(tool=Tool.PAN_TO_FOCUS))
            near = await ex.observe()
            assert near.window.y < 500
        finally:
            await ex.close()

    asyncio.run(main())


def test_press_repeat_presses_for_real(site):
    async def body(ex):
        result = await ex.execute(Action(tool=Tool.PRESS, key="Tab", repeat=2))
        obs = await ex.observe()
        assert result.focus_after == _ref(obs.content, "Add to cart")
        assert [e.target for e in result.events if e.type == "keydown"] == ["Tab", "Tab"]

    _run(site, body)


def test_tabindex_minus_one_containers_do_not_hide_their_content(site):
    async def body(ex):
        await ex.execute(Action(tool=Tool.GOTO, url="/wrapped.html"))
        obs = await ex.observe()
        assert 'link "First result"' in obs.content and 'button "Filter"' in obs.content
        assert "# Results" in obs.content
        assert "[e1] main" not in obs.content and "clickable" not in obs.content

    _run(site, body)
