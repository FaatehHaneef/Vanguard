"""Gemini provider: one forced function call per step.

Works through the configured models and keys in turn. A key refused for quota is
rested, as in the team's earlier Gemini clients. If nothing answers, the caller gets
ProviderUnavailable and records the step as a model failure; there is no silent fallback
to a different behaviour, because that would change what is being measured.
"""

import asyncio
import json
import time

from google import genai
from google.genai import errors, types

from vanguard.contracts import Tool

from .base import JsonReply, ModelReply, ModelRequest, ProviderUnavailable
from .tools import description, json_schema, to_action

AUTH_REST_SECONDS = 600  # a key refused outright (401/403) is left alone for a while
RATE_REST_SECONDS = 65  # a key over its per-minute quota (429) is tried again after a minute
MAX_WAIT_SECONDS = 150  # how long to wait for a key to come back before giving up


class GeminiProvider:
    name = "gemini"

    def __init__(self, api_keys: list[str], models: list[str]):
        if not api_keys:
            raise ProviderUnavailable("No Gemini API key is configured (VANGUARD_GEMINI_API_KEYS).")
        self.keys = list(api_keys)
        self.models = list(models)
        # (model, key) -> time it may be used again. Quotas are per model and project.
        self.resting: dict[tuple[str, str], float] = {}
        self._next = 0  # round-robin position, so load spreads over all keys

    def _declarations(self, names: list[str]) -> list[types.FunctionDeclaration]:
        return [
            types.FunctionDeclaration(
                name=name,
                description=description(Tool(name)),
                parameters_json_schema=json_schema(Tool(name)),
            )
            for name in names
        ]

    async def next_action(self, request: ModelRequest) -> ModelReply:
        config = types.GenerateContentConfig(
            system_instruction=request.system,
            tools=[types.Tool(function_declarations=self._declarations(request.tool_names))],
            tool_config=types.ToolConfig(
                function_calling_config=types.FunctionCallingConfig(mode="ANY")
            ),
            temperature=0.7,
            seed=request.seed,
            automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
        )
        response, model, latency = await self._generate(request.user, config)
        return self._reply(response, model, latency)

    async def generate_json(self, system: str, user: str, schema: dict) -> JsonReply:
        """One JSON answer matching `schema` (Gemini's OpenAPI-style schema)."""
        config = types.GenerateContentConfig(
            system_instruction=system,
            response_mime_type="application/json",
            response_schema=schema,
            temperature=0.4,
        )
        response, model, latency = await self._generate(user, config)
        usage = response.usage_metadata
        try:
            value = json.loads(response.text or "")
            problem = None if isinstance(value, dict) else "reply is not an object"
        except json.JSONDecodeError as error:
            value, problem = None, f"reply is not JSON: {error.msg}"
        return JsonReply(
            value=value if problem is None else None,
            model=model,
            error=problem,
            latency_ms=latency,
            input_tokens=(usage.prompt_token_count or 0) if usage else 0,
            output_tokens=(usage.candidates_token_count or 0) if usage else 0,
        )

    async def _generate(self, contents: str, config: types.GenerateContentConfig):
        """Try each model with the keys in round-robin order; return (response, model, ms).

        Keys over their per-minute quota rest briefly. If every key of every model is
        resting, wait for the first to come back (up to MAX_WAIT_SECONDS) rather than
        failing the run on a short burst.
        """
        deadline = time.time() + MAX_WAIT_SECONDS
        while True:
            last_problem = "no model answered"
            for model in self.models:
                for offset in range(len(self.keys)):
                    key = self.keys[(self._next + offset) % len(self.keys)]
                    if self.resting.get((model, key), 0) > time.time():
                        continue
                    started = time.perf_counter()
                    try:
                        client = genai.Client(api_key=key)
                        response = await client.aio.models.generate_content(
                            model=model, contents=contents, config=config
                        )
                    except errors.APIError as error:
                        if error.code in (429, 503):  # quota, or the model is overloaded
                            self.resting[(model, key)] = time.time() + RATE_REST_SECONDS
                            last_problem = f"all keys over quota or busy ({error.code})"
                            continue
                        if error.code in (401, 403):
                            self.resting[(model, key)] = time.time() + AUTH_REST_SECONDS
                            last_problem = f"key refused ({error.code})"
                            continue
                        last_problem = f"{model} error {error.code}"
                        break  # try the next model
                    self._next = (self.keys.index(key) + 1) % len(self.keys)
                    return response, model, (time.perf_counter() - started) * 1000
            soonest = min(self.resting.values(), default=0)
            if not self.resting or soonest > deadline or "error" in last_problem:
                raise ProviderUnavailable(last_problem)
            await asyncio.sleep(max(1.0, soonest - time.time()))

    @staticmethod
    def _reply(response: types.GenerateContentResponse, model: str, latency: float) -> ModelReply:
        usage = response.usage_metadata
        tokens_in = (usage.prompt_token_count or 0) if usage else 0
        tokens_out = (usage.candidates_token_count or 0) if usage else 0
        calls = response.function_calls or []
        if not calls:
            return ModelReply(
                action=None,
                model=model,
                error="no tool call in reply",
                latency_ms=latency,
                input_tokens=tokens_in,
                output_tokens=tokens_out,
            )
        call = calls[0]
        action, problem = to_action(call.name, dict(call.args or {}))
        return ModelReply(
            action=action,
            model=model,
            raw={"name": call.name, "args": dict(call.args or {})},
            error=problem,
            latency_ms=latency,
            input_tokens=tokens_in,
            output_tokens=tokens_out,
        )
