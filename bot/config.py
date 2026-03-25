"""Configuration loading from environment variables."""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


# Find .env.bot.secret - try multiple locations
def get_env_file() -> str:
    """Get the path to .env.bot.secret file."""
    # Try parent directory (project root)
    env_file = Path(__file__).resolve().parent.parent / ".env.bot.secret"
    if env_file.exists():
        return str(env_file)
    # Try current working directory
    env_file = Path.cwd() / ".env.bot.secret"
    if env_file.exists():
        return str(env_file)
    # Fallback to empty string (will use environment variables only)
    return ""


env_file_path = get_env_file()


class BotSettings(BaseSettings):
    """Bot configuration loaded from environment variables."""

    # Telegram bot token
    BOT_TOKEN: str = ""

    # LMS API configuration
    LMS_API_BASE_URL: str = ""
    LMS_API_KEY: str = ""

    # LLM API configuration (for Task 3: intent routing)
    LLM_API_KEY: str = ""
    LLM_API_BASE_URL: str = ""
    LLM_API_MODEL: str = "coder-model"

    model_config = SettingsConfigDict(
        env_file=env_file_path,
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="allow",
    )


# Global settings instance
settings = BotSettings.model_validate({})
