"""Any OpenAI-compatible chat API: Ollama, LM Studio, Groq, OpenAI, and others.

One forced tool call per step, as with Gemini (tool_choice "required"). Local runs use
this to compare models (alternative a); the deployed app enables Gemini only.

Configured in Settings.openai_compatible, by name, for example:
    {"ollama": {"base_url": "http://localhost:11434/v1", "model": "qwen2.5:7b"},
     "groq":   {"base_url": "https://api.groq.com/openai/v1", "model": "...",
                "api_key": "..."}}
"""

import json
import time

import httpx

from vanguard.contracts import Tool

from .base import JsonReply, ModelReply, ModelRequest, ProviderUnavailable
from .tools import description, json_schema, to_action

TIMEOUT_SECONDS = 120


def _schema_to_json_schema(schema: dict) -> dict:
    """Gemini's OpenAPI-style schema (types in capitals) as plain JSON Schema."""
    out = {}
    for key, value in schema.items():
        if key == "type" and isinstance(value, str):
            out[key] = value.lower()
        elif isinstance(value, dict):
            out[key] = (
                _schema_to_json_schema(value)
                if key != "properties"
                else {name: _schema_to_json_schema(sub) for name, sub in value.items()}
            )
        else:
            out[key] = value
    return out


class OpenAICompatibleProvider:
    def __init__(
        self,
        name: str,
        base_url: str,
        model: str,
        api_key: str = "",
        temperature: float = 0.7,
        transport: httpx.AsyncBaseTransport | None = None,
    ):
        self.name = name
        self.model = model
        self.temperature = temperature
        headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
        self._client = httpx.AsyncClient(
            base_url=base_url.rstrip("/"),
            headers=headers,
            timeout=TIMEOUT_SECONDS,
            transport=transport,
        )

    async def _post(self, body: dict) -> tuple[dict, float]:
        started = time.perf_counter()
        try:
            response = await self._client.post("/chat/completions", json=body)
        except httpx.HTTPError as error:
            raise ProviderUnavailable(f"{self.name}: {type(error).__name__}") from None
        if response.status_code in (401, 403, 429) or response.status_code >= 500:
            raise ProviderUnavailable(f"{self.name}: HTTP {response.status_code}")
        if response.status_code >= 400:
            raise ProviderUnavailable(
                f"{self.name}: HTTP {response.status_code} {response.text[:200]}"
            )
        return response.json(), (time.perf_counter() - started) * 1000

    async def next_action(self, request: ModelRequest) -> ModelReply:
        tools = [
            {
                "type": "function",
                "function": {
                    "name": name,
                    "description": description(Tool(name)),
                    "parameters": json_schema(Tool(name)),
                },
            }
            for name in request.tool_names
        ]
        body = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": request.system},
                {"role": "user", "content": request.user},
            ],
            "tools": tools,
            "tool_choice": "required",
            "temperature": self.temperature,
            "seed": request.seed,
        }
        data, latency = await self._post(body)
        usage = data.get("usage") or {}
        tokens_in, tokens_out = usage.get("prompt_tokens", 0), usage.get("completion_tokens", 0)
        message = ((data.get("choices") or [{}])[0]).get("message") or {}
        calls = message.get("tool_calls") or []
        if not calls:
            return ModelReply(
                action=None,
                model=self.model,
                error="no tool call in reply",
                latency_ms=latency,
                input_tokens=tokens_in,
                output_tokens=tokens_out,
            )
        function = calls[0].get("function") or {}
        try:
            args = json.loads(function.get("arguments") or "{}")
        except json.JSONDecodeError:
            args, problem = {}, "tool arguments are not JSON"
        else:
            problem = None
        action, invalid = to_action(
            function.get("name", ""), args if isinstance(args, dict) else {}
        )
        return ModelReply(
            action=action if problem is None else None,
            model=self.model,
            raw={"name": function.get("name"), "args": args},
            error=problem or invalid,
            latency_ms=latency,
            input_tokens=tokens_in,
            output_tokens=tokens_out,
        )

    async def generate_json(self, system: str, user: str, schema: dict) -> JsonReply:
        instructions = (
            f"{system}\n\nAnswer with one JSON object that matches this JSON Schema:\n"
            f"{json.dumps(_schema_to_json_schema(schema))}"
        )
        body = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": instructions},
                {"role": "user", "content": user},
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.4,
        }
        data, latency = await self._post(body)
        usage = data.get("usage") or {}
        content = (((data.get("choices") or [{}])[0]).get("message") or {}).get("content") or ""
        try:
            value = json.loads(content)
            problem = None if isinstance(value, dict) else "reply is not an object"
        except json.JSONDecodeError as error:
            value, problem = None, f"reply is not JSON: {error.msg}"
        return JsonReply(
            value=value if problem is None else None,
            model=self.model,
            error=problem,
            latency_ms=latency,
            input_tokens=usage.get("prompt_tokens", 0),
            output_tokens=usage.get("completion_tokens", 0),
        )
