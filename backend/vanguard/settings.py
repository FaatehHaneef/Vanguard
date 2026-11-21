"""Configuration, read from the environment (and a local .env file in development).

Nothing secret has a default. Paths that live outside the repository, such as the
dataset folder, are always configured here and never hard-coded elsewhere.
"""

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="VANGUARD_", extra="ignore")

    env: str = Field("development", description="development, test or production")
    database_url: str = "sqlite:///./vanguard-dev.db"
    data_dir: Path = Path("D:/VanguardData")

    # Model providers. The deployed app uses Gemini only; local runs may offer others.
    default_provider: str = "gemini"
    enabled_providers: list[str] = ["gemini", "fake"]
    gemini_api_keys: list[str] = []
    gemini_models: list[str] = ["gemini-flash-latest", "gemini-flash-lite-latest"]

    # Where the worker is allowed to send the browser. Anything else is blocked by the gate.
    allowed_origins: list[str] = ["http://localhost:3100"]
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
    # Inside Docker the sites are not on localhost. Requests to a key origin are sent to
    # the value origin instead, while the page keeps its usual address, for example
    # {"http://localhost:3100": "http://tallowmere:3100"}.
    origin_rewrites: dict[str, str] = {}
    # Screenshots of every observation, saved under data_dir/screenshots/<session>/.
    screenshots: bool = True
    cors_origins: list[str] = ["http://localhost:3000"]

    # Model price per million tokens, for cost per run. 0 means free tier; set from the
    # provider's current price list, never guessed.
    price_in_per_mtok: float = 0.0
    price_out_per_mtok: float = 0.0

    max_steps_per_run: int = 40
    stuck_after_steps: int = 5


@lru_cache
def get_settings() -> Settings:
    return Settings()
