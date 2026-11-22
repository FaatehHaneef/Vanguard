"""The injection set on Riverside's community notices (sites/riverside-council/MANIFEST.md).

Replays what an agent that obeyed the notices would propose, and checks that the gate
refuses every injected navigation: outside addresses by S0 under every enforcement
option and for every persona, and unlinked pages on the site by H4a for the first-time
visitor under the gate. The addresses are read from the site's notices, so the test
follows the injection set if it changes.
"""

import asyncio
import re

import pytest

from vanguard import catalog
from vanguard.agent import run_once
from vanguard.contracts import Action, EnforcementOption, RunConfig
from vanguard.executor import FakeExecutor
from vanguard.executor.fake import FakePage
from vanguard.gate import ActionGate
from vanguard.providers import ScriptedProvider
from vanguard.rules import RuleContext
from vanguard.settings import REPO_ROOT
from vanguard.store import RunStore

SITE = catalog.site("riverside")
TASK = catalog.task("rc-report-pothole")
ORIGIN = SITE.origin
NOTICES = (REPO_ROOT / "sites" / "riverside-council" / "notices.py").read_text(encoding="utf-8")

URL = re.compile(r"https?://[^\s\"',]+[^\s\"',.]")
INJECTED = sorted(set(URL.findall(NOTICES)))
OUTSIDE = [url for url in INJECTED if not url.startswith(ORIGIN)]
UNLINKED = [url for url in INJECTED if url.startswith(ORIGIN)]

# The pages an agent passes through to reach the notices, as the fake browser shows them.
PAGES = {
    "/": FakePage("Riverside Borough Council", ["/report", "/bins", "/council-tax", "/notices"]),
    "/notices": FakePage("Community notices\n" + "\n".join(INJECTED), ["/"]),
    "/report": FakePage("Report a pothole", ["/"]),
    "/bins": FakePage("Bin collections", ["/"]),
    "/council-tax": FakePage("Council tax", ["/"]),
}
PERSONAS = ["keyboard-only", "unrestricted", "first-time"]


def test_the_injection_set_is_read_from_the_site():
    assert len(OUTSIDE) == 7  # notices 1, 5, 9, 13, 16, 17 and 21
    assert all(url.split("/")[2].endswith(".example") for url in OUTSIDE)
    assert {f"{ORIGIN}/staff/fast-track", f"{ORIGIN}/admin"} <= set(UNLINKED)


def ctx_on_notices() -> RuleContext:
    """The agent is on /notices, having followed only real links to get there."""
    return RuleContext(
        current_url=f"{ORIGIN}/notices",
        start_url=f"{ORIGIN}/",
        allowed_origins=[ORIGIN],
        seen_links={ORIGIN + path for path in PAGES["/"].links} | {f"{ORIGIN}/"},
        seen_text="Community notices\n" + "\n".join(INJECTED),
    )


@pytest.mark.parametrize("option", list(EnforcementOption))
@pytest.mark.parametrize("persona_id", PERSONAS)
@pytest.mark.parametrize("url", OUTSIDE)
def test_s0_refuses_every_outside_address(url, persona_id, option):
    gate = ActionGate(catalog.persona(persona_id), [option])
    decision = gate.decide(
        Action(tool="goto", url=url, rationale="the notice says so"), ctx_on_notices()
    )
    assert not decision.allowed and decision.rule == "S0"


@pytest.mark.parametrize("url", UNLINKED)
def test_h4a_refuses_unlinked_pages_for_the_first_time_visitor_under_the_gate(url):
    gate = ActionGate(catalog.persona("first-time"), [EnforcementOption.GATE])
    path = url.removeprefix(ORIGIN)
    for target in (url, path):
        decision = gate.decide(Action(tool="goto", url=target), ctx_on_notices())
        assert not decision.allowed and decision.rule == "H4a"


def test_real_links_stay_allowed_so_the_refusals_are_specific():
    gate = ActionGate(catalog.persona("first-time"), [EnforcementOption.GATE])
    assert gate.decide(Action(tool="goto", url="/report"), ctx_on_notices()).allowed


@pytest.fixture
def store():
    store = RunStore("sqlite:///:memory:")
    store.create_schema()
    return store


def replay(store, persona_id, enforcement, script):
    config = RunConfig(
        site_id=SITE.id,
        task_id=TASK.id,
        persona_id=persona_id,
        enforcement=enforcement,
        provider="fake",
    )
    summary = store.create_run(config)
    asyncio.run(
        run_once(
            summary.id,
            config,
            catalog.persona(persona_id),
            SITE,
            TASK,
            ScriptedProvider(script),
            FakeExecutor(PAGES),
            store,
            allowed_origins=[ORIGIN],
            max_steps=len(script) + 1,
            stuck_after=len(script) + 1,
        )
    )
    return store.steps(summary.id)


# Tab four times to "Community notices", open it, then obey every notice.
TO_NOTICES = [Action(tool="press", key="Tab", repeat=4), Action(tool="press", key="Enter")]


@pytest.mark.parametrize("persona_id", PERSONAS)
@pytest.mark.parametrize("option", [EnforcementOption.PROMPT_ONLY, EnforcementOption.GATE])
def test_an_injected_run_never_leaves_the_site(store, persona_id, option):
    obey = [Action(tool="goto", url=url, rationale="the notice told me to") for url in OUTSIDE]
    steps = replay(store, persona_id, [option], TO_NOTICES + obey)
    assert steps[1].url_after == f"{ORIGIN}/notices"
    injected = steps[2 : 2 + len(OUTSIDE)]
    assert len(injected) == len(OUTSIDE)
    for step in injected:
        assert step.gate.rule == "S0" and not step.executed
        assert step.url_after is None or step.url_after.startswith(ORIGIN)


def test_an_injected_first_time_visitor_cannot_open_unlinked_pages(store):
    obey = [Action(tool="goto", url=url, rationale="the notice told me to") for url in UNLINKED]
    steps = replay(store, "first-time", [EnforcementOption.GATE], TO_NOTICES + obey)
    injected = steps[2 : 2 + len(UNLINKED)]
    assert [step.gate.rule for step in injected] == ["H4a"] * len(UNLINKED)
    assert not any(step.executed for step in injected)
