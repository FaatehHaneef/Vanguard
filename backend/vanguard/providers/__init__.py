"""Model providers behind one interface (see base.py).

The deployed app enables Gemini only. Local runs may enable others through
VANGUARD_ENABLED_PROVIDERS: any OpenAI-compatible API (Ollama, LM Studio, Groq, OpenAI)
is configured by name in VANGUARD_OPENAI_COMPATIBLE.
"""

from vanguard.settings import Settings

from .base import JsonReply, ModelReply, ModelRequest, Provider, ProviderUnavailable
from .fake import ScriptedProvider


def make_provider(name: str, settings: Settings) -> Provider:
    if name not in settings.enabled_providers:
        raise ProviderUnavailable(f"Provider {name!r} is not enabled in this deployment.")
    if name == "gemini":
        from .gemini import GeminiProvider

        return GeminiProvider(settings.gemini_api_keys, settings.gemini_models)
    if name == "fake":
        return ScriptedProvider()
    if name in settings.openai_compatible:
        from .openai_compatible import OpenAICompatibleProvider

        config = settings.openai_compatible[name]
        return OpenAICompatibleProvider(
            name,
            base_url=config["base_url"],
            model=config["model"],
            api_key=config.get("api_key", ""),
        )
    raise ProviderUnavailable(f"Provider {name!r} is not implemented yet.")


__all__ = [
    "JsonReply",
    "ModelReply",
    "ModelRequest",
    "Provider",
    "ProviderUnavailable",
    "ScriptedProvider",
    "make_provider",
]
