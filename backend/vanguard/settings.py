"""Configuration, read from the environment (and a local .env file in development).

Nothing secret has a default. Paths that live outside the repository, such as the
dataset folder, are always configured here and never hard-coded elsewhere.
"""

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

REPO_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    # The repository root's .env, wherever the command is run from; a local .env overrides it.
    model_config = SettingsConfigDict(
        env_file=(REPO_ROOT / ".env", ".env"), env_prefix="VANGUARD_", extra="ignore"
    )

    env: str = Field("development", description="development, test or production")
    database_url: str = "sqlite:///./vanguard-dev.db"
    data_dir: Path = Path("D:/VanguardData")

    # Model providers. The deployed app uses Gemini only; local runs may offer others.
    default_provider: str = "gemini"
    enabled_providers: list[str] = ["gemini", "fake"]
    gemini_api_keys: list[str] = []
    # Current model IDs (ai.google.dev pricing page, read 2026-11-22), tried in order. Keep
    # one model per experiment so results never mix models; every step records the model.
    gemini_models: list[str] = ["gemini-3.8-flash"]
    # OpenAI-compatible providers by name (local runs only), for example
    # {"ollama": {"base_url": "http://localhost:11434/v1", "model": "qwen2.5:7b"}}.
    # Each name must also be listed in enabled_providers.
    openai_compatible: dict[str, dict[str, str]] = {}

    # Where the worker may send the browser; anything else is blocked by the gate. Every
    # catalog site (built-in or custom) is always allowed (vanguard.origins); list only
    # additional origins here.
    allowed_origins: list[str] = []
    # Payment providers the agent may reach, sandbox hosts only.
    allowed_payment_hosts: list[str] = [
        "sandbox.braintreegateway.com",
        "assets.braintreegateway.com",
        "client-analytics.sandbox.braintreegateway.com",
        "payments.sandbox.braintree-api.com",
        "api.sandbox.braintreegateway.com",
    ]

    # "playwright" drives a real browser; "fake" uses the in-memory test site.
    executor: str = "fake"
    headless: bool = True
    # The decorative character overlay (apps/hud) in the test browser and screenshots.
    hud: bool = True
    # Stream the test browser to the run page while a run goes (vanguard.live).
    live_view: bool = True
    # Inside Docker the sites are not on localhost. Requests to a key origin are sent to
    # the value origin instead, while the page keeps its usual address, for example
    # {"http://localhost:3100": "http://tallowmere:3100"}.
    origin_rewrites: dict[str, str] = {}
    # Inside Docker Compose: route each catalog site's origin to its service (Site.docker_host).
    in_docker: bool = False
    # Screenshots of every observation, saved under data_dir/screenshots/<session>/.
    screenshots: bool = True
    cors_origins: list[str] = ["http://localhost:3000"]

    # Model price per million tokens, for cost per run. 0 means free tier; set from the
    # provider's current price list, never guessed.
    price_in_per_mtok: float = 0.0
    price_out_per_mtok: float = 0.0

    max_steps_per_run: int = 40
    # The model may return up to this many actions in one call (tool calls in order).
    # Each is gated and recorded as its own step; 1 restores one action per call.
    actions_per_call: int = 4
    # Free-tier requests per key, per model, per day (Pacific time), for `cli usage`.
    calls_per_key_per_day: int = 20
    stuck_after_steps: int = 5


@lru_cache
def get_settings() -> Settings:
    return Settings()
