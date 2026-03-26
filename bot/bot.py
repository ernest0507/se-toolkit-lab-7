"""Entry point for Telegram bot with optional test mode."""

import argparse
import asyncio
import sys

from handlers.commands import handle_message


def get_arguments() -> argparse.Namespace:
    """Configure and retrieve CLI arguments."""
    arg_parser = argparse.ArgumentParser(description="LMS Telegram Bot")

    arg_parser.add_argument(
        "--test",
        dest="test_message",
        type=str,
        metavar="MESSAGE",
        help="Run in test mode with provided message (e.g., '/start')",
    )

    return arg_parser.parse_args()


async def process_test(message: str) -> None:
    """Process a single message in test mode."""
    result = await handle_message(message)
    print(result)


async def run() -> None:
    """Program entry logic."""
    options = get_arguments()

    if options.test_message is not None:
        await process_test(options.test_message)
        sys.exit()

    # Placeholder for future Telegram bot launch
    print("Telegram mode is not implemented yet. Use --test.")
    sys.exit()


if __name__ == "__main__":
    asyncio.run(run())
