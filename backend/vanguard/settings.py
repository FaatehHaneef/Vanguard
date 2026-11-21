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
    ]

    max_steps_per_run: int = 40
    stuck_after_steps: int = 5


@lru_cache
def get_settings() -> Settings:
    return Settings()
