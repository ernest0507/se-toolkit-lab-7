"""Inline keyboard definitions for the Telegram bot."""

from typing import Any

# Inline keyboard for /start command
START_KEYBOARD = {
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

# Keyboard for lab selection
LABS_KEYBOARD = {
    "inline_keyboard": [
        [{"text": "Lab 01", "callback_data": "lab_01"}],
        [{"text": "Lab 02", "callback_data": "lab_02"}],
        [{"text": "Lab 03", "callback_data": "lab_03"}],
        [{"text": "Lab 04", "callback_data": "lab_04"}],
        [{"text": "Lab 05", "callback_data": "lab_05"}],
        [{"text": "Lab 06", "callback_data": "lab_06"}],
        [{"text": "Lab 07", "callback_data": "lab_07"}],
    ]
}

# Keyboard for common queries
QUICK_ACTIONS_KEYBOARD = {
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
    """Get the keyboard for /start command."""
    return START_KEYBOARD


def get_labs_keyboard() -> dict[str, Any]:
    """Get the keyboard for lab selection."""
    return LABS_KEYBOARD


def get_quick_actions_keyboard() -> dict[str, Any]:
    """Get the keyboard for quick actions."""
    return QUICK_ACTIONS_KEYBOARD
