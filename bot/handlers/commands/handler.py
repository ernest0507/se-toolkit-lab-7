"""Command handling logic for LMS Telegram bot."""

import sys
from pathlib import Path

# Ensure parent directory is in sys.path for service imports
BASE_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

from services.lms_api import get_api_client, APIError
from services.intent_router import get_router
from keyboards import get_start_keyboard, get_quick_actions_keyboard


# Initialize shared services
_api = get_api_client()
_router = get_router()

# Store last keyboard state
_current_keyboard: dict | None = None


def get_last_keyboard() -> dict | None:
    """Return the last keyboard used."""
    return _current_keyboard


def _update_keyboard(kb: dict | None) -> None:
    """Update keyboard state."""
    global _current_keyboard
    _current_keyboard = kb


async def handle_message(message: str) -> str:
    """Main message dispatcher."""
    text = message.strip()

    commands_map = {
        "/start": handle_start,
        "/help": handle_help,
        "/health": handle_health,
        "/labs": handle_labs,
    }

    if text in commands_map:
        return await commands_map[text]()

    if text.startswith("/scores"):
        _, *rest = text.split(maxsplit=1)
        lab_id = rest[0] if rest else ""
        return await handle_scores(lab_id)

    return await handle_natural_language(text)


async def handle_start() -> str:
    """Start command handler."""
    _update_keyboard(get_start_keyboard())
    return (
        "Welcome to the LMS Bot! 🎓\n\n"
        "I can help you explore lab data, scores, and analytics.\n\n"
        "Try asking me:\n"
        "• What labs are available?\n"
        "• Show scores for lab 4\n"
        "• Which lab has the lowest pass rate?\n"
        "• Who are the top students?\n\n"
        "Commands: /help, /health, /labs, /scores <lab>"
    )


async def handle_help() -> str:
    """Help command handler."""
    _update_keyboard(get_start_keyboard())
    return (
        "Commands:\n"
        "/start - Welcome\n"
        "/help - This help\n"
        "/health - Backend status\n"
        "/labs - List labs\n"
        "/scores <lab> - Lab stats\n\n"
        "You can also ask questions in plain English."
    )


async def handle_health() -> str:
    """Health check handler."""
    try:
        items = await _api.get_items()
        return f"Backend is healthy. {len(items)} items available."
    except APIError as err:
        return f"Backend error: {err.message}"


async def handle_labs() -> str:
    """Labs listing handler."""
    try:
        items = await _api.get_items()
        labs = [x for x in items if x.type == "lab"]

        if not labs:
            return "No labs available."

        return "Available labs:\n" + "\n".join(f"- {lab.title}" for lab in labs)

    except APIError as err:
        return f"Backend error: {err.message}"


async def handle_scores(lab: str) -> str:
    """Scores handler for a specific lab."""
    if not lab:
        return "Usage: /scores <lab> (e.g., /scores lab-04)"

    try:
        stats = await _api.get_pass_rates(lab)

        if not stats:
            return f"No pass rate data available for {lab}."

        result = [f"Pass rates for {lab}:"]
        result.extend(
            f"- {r.task}: {r.pass_rate:.1f}% ({r.attempts} attempts)"
            for r in stats
        )

        return "\n".join(result)

    except APIError as err:
        return f"Backend error: {err.message}"


async def handle_natural_language(message: str) -> str:
    """Handle free-form queries via LLM router."""
    _update_keyboard(get_quick_actions_keyboard())

    try:
        return await _router.route(message)
    except Exception as err:
        return (
            "I couldn’t process that request.\n"
            "Try asking about labs, scores, or pass rates.\n\n"
            f"Details: {err}"
        )
