"""Load application configuration from environment variables."""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


def _resolve_env_path() -> str:
    """Locate .env.bot.secret file in possible locations."""
    possible_paths = [
        Path(__file__).resolve().parent.parent / ".env.bot.secret",
        Path.cwd() / ".env.bot.secret",
    ]

    for path in possible_paths:
        if path.exists():
            return str(path)

    return ""  # fallback: rely only on system env vars


_ENV_PATH = _resolve_env_path()


class BotConfig(BaseSettings):
    """Application settings pulled from environment variables."""

    # Telegram
    BOT_TOKEN: str = ""

    # LMS backend
    LMS_API_BASE_URL: str = ""
    LMS_API_KEY: str = ""

    # LLM settings (used for intent routing)
    LLM_API_KEY: str = ""
    LLM_API_BASE_URL: str = ""
    LLM_API_MODEL: str = "coder-model"

    model_config = SettingsConfigDict(
        env_file=_ENV_PATH,
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="allow",
    )


# Instantiate global config
config = BotConfig.model_validate({})
