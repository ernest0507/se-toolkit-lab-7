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
