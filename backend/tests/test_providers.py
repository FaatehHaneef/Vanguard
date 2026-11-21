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
