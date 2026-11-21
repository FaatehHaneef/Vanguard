"""Model providers behind one interface (see base.py).

The deployed app enables Gemini only. Local runs may enable others through
VANGUARD_ENABLED_PROVIDERS; a local model (Ollama), Groq and OpenAI are planned.
"""

from vanguard.settings import Settings

from .base import ModelReply, ModelRequest, Provider, ProviderUnavailable
from .fake import ScriptedProvider


def make_provider(name: str, settings: Settings) -> Provider:
    if name not in settings.enabled_providers:
        raise ProviderUnavailable(f"Provider {name!r} is not enabled in this deployment.")
    if name == "gemini":
        from .gemini import GeminiProvider

        return GeminiProvider(settings.gemini_api_keys, settings.gemini_models)
    if name == "fake":
        return ScriptedProvider()
    raise ProviderUnavailable(f"Provider {name!r} is not implemented yet.")


__all__ = [
    "ModelReply",
    "ModelRequest",
    "Provider",
    "ProviderUnavailable",
    "ScriptedProvider",
    "make_provider",
]
