# LMS Telegram Bot Development Plan

## Overview

This document describes the development plan for a Telegram bot designed for LMS. The bot allows students to access information about their lab progress, scores, and course details directly via Telegram. It communicates with the LMS backend API and leverages an LLM for interpreting natural language queries and routing intents.

## Architecture

The project is organized using a **layered architecture**, ensuring a clear separation of responsibilities:

1. **Entry Point** (`bot.py`): Manages application startup and provides a `--test` mode for offline interaction
2. **Handlers** (`handlers/`): Pure logic functions that process requests and return text responses, independent of Telegram
3. **Services** (`services/`): Responsible for communication with external systems (LMS API, LLM API)
4. **Configuration** (`config.py`): Handles environment variables using pydantic-settings

This handler-based approach (**P0.1**) ensures that the same logic can be reused across different environments: test mode, unit tests, and Telegram integration — keeping transport separate from business logic.

## Task Breakdown

### Task 1: Scaffold (Current)

Set up the initial project structure with support for `--test` mode.  
At this stage, handlers return placeholder responses.  
The main goal is to ensure that running:



produces a valid output without requiring Telegram credentials.

### Task 2: Backend Integration

Integrate the bot with the LMS backend API:

- `/health` — verify connectivity via `/api/ping`
- `/labs` — retrieve available labs from `/api/items`
- `/scores` — obtain user scores from the backend

Implement an API client using Bearer token authentication.  
Ensure proper error handling for network issues, authentication failures (401/403), and timeouts.

### Task 3: Intent Routing with LLM

Enable natural language interaction.  
Users should be able to ask questions like *"what labs are available?"* instead of using strict commands.

The LLM is used to map user input to the appropriate handler via tool descriptions.  
Key idea: **well-written tool descriptions are more important than complex prompt engineering**.

### Task 4: Deployment

Deploy the bot on a VM and configure process management (e.g., `nohup` or `systemd`).  
Make sure the bot continues running after SSH disconnection or system restart.  
Store sensitive environment variables securely, for example in `.env.bot.secret`.

## Testing Strategy

- **Test mode** — fast iteration using the `--test` flag  
- **Unit tests** — isolated testing of handlers (planned)  
- **Manual testing** — verification via Telegram after deployment  

## Environment Variables

| Variable | Description | Source |
|----------|------------|--------|
| `BOT_TOKEN` | Telegram bot token | BotFather |
| `LMS_API_BASE_URL` | Backend API URL | Docker config |
| `LMS_API_KEY` | Backend API key | `.env.docker.secret` |
| `LLM_API_KEY` | LLM API key | Qwen Code / OpenRouter |
| `LLM_API_BASE_URL` | LLM API endpoint | Qwen Code / OpenRouter |
