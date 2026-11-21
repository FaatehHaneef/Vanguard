"""Gemini provider: one forced function call per step.

Works through the configured models and keys in turn. A key refused for quota is
rested, as in the team's earlier Gemini clients. If nothing answers, the caller gets
ProviderUnavailable and records the step as a model failure; there is no silent fallback
to a different behaviour, because that would change what is being measured.
"""

import time

from google import genai
from google.genai import errors, types

from vanguard.contracts import Tool

from .base import ModelReply, ModelRequest, ProviderUnavailable
from .tools import description, json_schema, to_action

KEY_REST_SECONDS = 600


class GeminiProvider:
    name = "gemini"

    def __init__(self, api_keys: list[str], models: list[str]):
        if not api_keys:
            raise ProviderUnavailable("No Gemini API key is configured (VANGUARD_GEMINI_API_KEYS).")
        self.keys = list(api_keys)
        self.models = list(models)
        self.resting: dict[str, float] = {}

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
        last_problem = "no model answered"
        for model in self.models:
            for key in self.keys:
                if self.resting.get(key, 0) > time.time():
                    continue
                started = time.perf_counter()
                try:
                    client = genai.Client(api_key=key)
                    response = await client.aio.models.generate_content(
                        model=model, contents=request.user, config=config
                    )
                except errors.APIError as error:
                    if error.code in (401, 403, 429):
                        self.resting[key] = time.time() + KEY_REST_SECONDS
                        last_problem = f"key refused ({error.code})"
                        continue
                    last_problem = f"{model} error {error.code}"
                    break  # try the next model
                latency = (time.perf_counter() - started) * 1000
                return self._reply(response, model, latency)
        raise ProviderUnavailable(last_problem)

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
