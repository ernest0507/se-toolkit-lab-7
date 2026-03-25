# Dockerfile for the LMS Telegram Bot
# Uses uv for dependency management (no requirements.txt or pip)

ARG REGISTRY_PREFIX=harbor.pg.innopolis.university/docker-hub-cache/

# ---
# Stage 1: Build the application
# ---
FROM ${REGISTRY_PREFIX}astral/uv:python3.14-bookworm-slim AS builder

ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

# Omit development dependencies
ENV UV_NO_DEV=1

# Use system Python interpreter
ENV UV_PYTHON_DOWNLOADS=0

WORKDIR /app

# Copy workspace files needed for uv sync
COPY pyproject.toml uv.lock /app/
COPY backend/pyproject.toml /app/backend/pyproject.toml
COPY bot/pyproject.toml /app/bot/pyproject.toml

# Sync dependencies (includes bot dependencies)
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-install-project

# Copy bot source code
COPY bot /app/bot

# Sync again to install bot project
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked

# ---
# Stage 2: Runtime image
# ---
FROM ${REGISTRY_PREFIX}python:3.14.2-slim-bookworm

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV LANG=C.UTF-8

# Create non-root user
RUN groupadd --system --gid 999 nonroot \
    && useradd --system --gid 999 --uid 999 --create-home nonroot

# Copy application from builder
COPY --from=builder --chown=nonroot:nonroot /app /app

# Add virtual environment to PATH
ENV PATH="/app/.venv/bin:$PATH"

# Use non-root user
USER nonroot

WORKDIR /app

# Run the bot
CMD ["python", "bot/bot.py"]
