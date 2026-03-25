# LMS Telegram Bot Development Plan

## Overview

This document outlines the development plan for the LMS Telegram Bot, which provides students with access to their lab progress, scores, and course information through Telegram. The bot communicates with the LMS backend API and uses an LLM for natural language intent routing.

## Architecture

The bot follows a **layered architecture** with clear separation of concerns:

1. **Entry Point** (`bot.py`): Handles Telegram bot lifecycle and `--test` mode for offline testing
2. **Handlers** (`handlers/`): Pure functions that process commands and return text responses — no Telegram dependency
3. **Services** (`services/`): API clients for external services (LMS API, LLM API)
4. **Configuration** (`config.py`): Environment variable loading with pydantic-settings

This **testable handler architecture** (P0.1) allows the same handler logic to work from `--test` mode, unit tests, or Telegram — the transport layer is separate from the business logic.

## Task Breakdown

### Task 1: Scaffold (Current)

Create the project skeleton with `--test` mode. Handlers return placeholder text. The key deliverable is a working test mode where `uv run bot.py --test "/start"` prints a response without needing Telegram credentials.

### Task 2: Backend Integration

Implement real API calls to the LMS backend:
- `/health` — Check backend connectivity via `/api/ping`
- `/labs` — Fetch available labs from `/api/items`
- `/scores` — Fetch student scores from the backend

Create an API client service with Bearer token authentication. Handle errors gracefully (network failures, 401/403, timeouts).

### Task 3: Intent Routing with LLM

Add natural language understanding. Instead of requiring exact commands like `/labs`, users can ask "what labs are available?" The bot uses an LLM to route intents to handlers via tool descriptions. Key insight: **description quality matters more than prompt engineering** — clear tool descriptions enable the LLM to make correct routing decisions.

### Task 4: Deployment

Deploy the bot on the VM with proper process management (nohup or systemd). Ensure the bot survives SSH disconnects and restarts. Configure environment variables securely via `.env.bot.secret`.

## Testing Strategy

- **Test mode**: `--test` flag for quick iteration without Telegram
- **Unit tests**: Test handlers in isolation (future)
- **Manual testing**: Deploy to VM and test in real Telegram

## Environment Variables

| Variable | Description | Source |
|----------|-------------|--------|
| `BOT_TOKEN` | Telegram bot token | BotFather |
| `LMS_API_BASE_URL` | Backend API URL | Docker config |
| `LMS_API_KEY` | Backend API key | `.env.docker.secret` |
| `LLM_API_KEY` | LLM API key | Qwen Code / OpenRouter |
| `LLM_API_BASE_URL` | LLM API endpoint | Qwen Code / OpenRouter |
