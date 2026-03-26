"""Definitions of inline keyboards used in the Telegram bot."""

from typing import Any


def _build_start_keyboard() -> dict[str, Any]:
    """Construct keyboard for the /start command."""
    return {
        "inline_keyboard": [
            [
                {"text": "📚 Available Labs", "callback_data": "labs"},
                {"text": "💊 Health Check", "callback_data": "health"},
            ],
            [
                {"text": "📊 Lab Scores", "callback_data": "scores_lab-04"},
                {"text": "🏆 Top Performers", "callback_data": "top_learners"},
            ],
            [
                {"text": "❓ Help", "callback_data": "help"},
            ],
        ]
    }


def _build_labs_keyboard() -> dict[str, Any]:
    """Construct keyboard for selecting labs."""
    labs = [f"{i:02d}" for i in range(1, 8)]

    return {
        "inline_keyboard": [
            [{"text": f"Lab {lab}", "callback_data": f"lab_{lab}"}]
            for lab in labs
        ]
    }


def _build_quick_actions_keyboard() -> dict[str, Any]:
    """Construct keyboard with quick actions."""
    return {
        "inline_keyboard": [
            [
                {"text": "📈 Pass Rates", "callback_data": "pass_rates"},
                {"text": "👥 Groups", "callback_data": "groups"},
            ],
            [
                {"text": "📅 Timeline", "callback_data": "timeline"},
                {"text": "✅ Completion", "callback_data": "completion"},
            ],
        ]
    }


def get_start_keyboard() -> dict[str, Any]:
    """Return start keyboard."""
    return _build_start_keyboard()


def get_labs_keyboard() -> dict[str, Any]:
    """Return labs keyboard."""
    return _build_labs_keyboard()


def get_quick_actions_keyboard() -> dict[str, Any]:
    """Return quick actions keyboard."""
    return _build_quick_actions_keyboard()
