import asyncio
import json

import httpx
import pytest

from vanguard.providers import ModelRequest, ProviderUnavailable, make_provider
from vanguard.providers.openai_compatible import OpenAICompatibleProvider
from vanguard.settings import Settings


def provider(handler):
    return OpenAICompatibleProvider(
        "local", "http://model.test/v1", "tiny", transport=httpx.MockTransport(handler)
    )


REQUEST = ModelRequest(system="s", user="u", tool_names=["press", "click"], seed=3)


def test_tool_call_becomes_an_action():
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen.update(json.loads(request.content))
        call = {"name": "press", "arguments": json.dumps({"key": "Tab", "rationale": "next"})}
        return httpx.Response(
            200,
            json={
                "choices": [{"message": {"tool_calls": [{"function": call}]}}],
                "usage": {"prompt_tokens": 12, "completion_tokens": 3},
            },
        )

    reply = asyncio.run(provider(handler).next_action(REQUEST))
    assert reply.action.tool == "press" and reply.action.key == "Tab"
    assert (reply.input_tokens, reply.output_tokens) == (12, 3)
    assert seen["tool_choice"] == "required" and seen["seed"] == 3
    assert [t["function"]["name"] for t in seen["tools"]] == ["press", "click"]


def test_bad_replies_and_outages():
    def no_call(request):
        return httpx.Response(200, json={"choices": [{"message": {"content": "hi"}}]})

    assert asyncio.run(provider(no_call).next_action(REQUEST)).error == "no tool call in reply"

    def broken_args(request):
        call = {"name": "press", "arguments": "{not json"}
        return httpx.Response(
            200, json={"choices": [{"message": {"tool_calls": [{"function": call}]}}]}
        )

    reply = asyncio.run(provider(broken_args).next_action(REQUEST))
    assert reply.action is None and "not JSON" in reply.error

    def limited(request):
        return httpx.Response(429)

    with pytest.raises(ProviderUnavailable):
        asyncio.run(provider(limited).next_action(REQUEST))


def test_json_generation():
    def handler(request):
        body = json.loads(request.content)
        assert body["response_format"] == {"type": "json_object"}
        assert '"type": "object"' in body["messages"][0]["content"]
        return httpx.Response(
            200, json={"choices": [{"message": {"content": '{"allowed": true}'}}]}
        )

    schema = {"type": "OBJECT", "properties": {"allowed": {"type": "BOOLEAN"}}}
    reply = asyncio.run(provider(handler).generate_json("sys", "user", schema))
    assert reply.value == {"allowed": True}


def test_configured_by_name():
    settings = Settings(
        enabled_providers=["ollama"],
        openai_compatible={"ollama": {"base_url": "http://localhost:11434/v1", "model": "m"}},
    )
    made = make_provider("ollama", settings)
    assert made.name == "ollama" and made.model == "m"
