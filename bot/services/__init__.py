"""Service modules for the LMS Telegram bot.

Services handle external API communication (LMS API, LLM API).
"""

from .intent_router import IntentRouter, get_router
from .llm_api import LLMClient, get_llm_client, TOOLS
from .lms_api import LMSAPIClient, get_api_client

__all__ = [
    "LMSAPIClient",
    "get_api_client",
    "LLMClient",
    "get_llm_client",
    "TOOLS",
    "IntentRouter",
    "get_router",
]
