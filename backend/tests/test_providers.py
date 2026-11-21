import asyncio

import pytest

from vanguard.contracts import Tool
from vanguard.providers import ModelRequest, ProviderUnavailable, ScriptedProvider, make_provider
from vanguard.providers.tools import all_tool_names, json_schema, to_action
from vanguard.settings import Settings


def test_every_tool_has_a_schema_with_rationale():
    assert set(all_tool_names()) == {tool.value for tool in Tool}
    for tool in Tool:
        assert "rationale" in json_schema(tool)["required"]


def test_to_action_accepts_valid_and_explains_invalid():
    action, problem = to_action("press", {"key": "Tab", "rationale": "next"})
    assert action is not None and problem is None
    action, problem = to_action("click", {"rationale": "oops"})
    assert action is None and "invalid tool call click" in problem


def test_scripted_provider_gives_up_when_script_ends():
    provider = ScriptedProvider()
    reply = asyncio.run(provider.next_action(ModelRequest("s", "u", all_tool_names())))
    assert reply.action.tool is Tool.GIVE_UP


def test_disabled_provider_is_refused():
    settings = Settings(enabled_providers=["gemini"], gemini_api_keys=["k"])
    with pytest.raises(ProviderUnavailable):
        make_provider("fake", settings)


def test_gemini_without_keys_is_unavailable():
    with pytest.raises(ProviderUnavailable):
        make_provider("gemini", Settings(enabled_providers=["gemini"], gemini_api_keys=[]))


def test_gemini_rotates_keys_rests_on_429_and_waits(monkeypatch):
    from google.genai import errors

    from vanguard.providers import gemini

    calls = []

    class FakeModels:
        def __init__(self, key):
            self.key = key

        async def generate_content(self, model, contents, config):
            calls.append((model, self.key))
            if self.key == "k1" and len(calls) == 1:
                raise errors.APIError(429, {"error": {"message": "slow down"}})
            return "response"

    class FakeClient:
        def __init__(self, api_key):
            self.aio = type("Aio", (), {"models": FakeModels(api_key)})()

    monkeypatch.setattr(gemini.genai, "Client", FakeClient)
    provider = gemini.GeminiProvider(["k1", "k2"], ["m"])
    response, model, _ = asyncio.run(provider._generate("hi", None))
    assert response == "response" and calls == [("m", "k1"), ("m", "k2")]
    assert provider.resting[("m", "k1")] > 0
    # Round robin: the next request starts at k1 again, which is resting, so k2 answers.
    asyncio.run(provider._generate("hi", None))
    assert calls[-1] == ("m", "k2") and len(calls) == 3

    # When every key is resting beyond the wait limit, the provider gives up.
    monkeypatch.setattr(gemini, "MAX_WAIT_SECONDS", 0)
    provider.resting = {("m", "k1"): 1e12, ("m", "k2"): 1e12}
    try:
        asyncio.run(provider._generate("hi", None))
    except gemini.ProviderUnavailable:
        pass
    else:
        raise AssertionError("expected ProviderUnavailable")
