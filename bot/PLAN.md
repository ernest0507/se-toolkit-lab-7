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

Enable natural language interaction.  
Users should be able to ask questions like *"what labs are available?"* instead of using strict commands.

The LLM is used to map user input to the appropriate handler via tool descriptions.  
Key idea: **well-written tool descriptions are more important than complex prompt engineering**.
| `LLM_API_BASE_URL` | LLM API endpoint | Qwen Code / OpenRouter |
