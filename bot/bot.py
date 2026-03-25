"""Telegram bot entry point with --test mode for offline testing."""

import argparse
import asyncio
import sys

from handlers.commands import handle_message


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="LMS Telegram Bot")
    parser.add_argument(
        "--test",
        type=str,
        metavar="MESSAGE",
        help="Test mode: pass a message (e.g., '/start') and print response to stdout",
    )
    return parser.parse_args()


async def handle_test_message(message: str) -> None:
    """Handle a test message and print response to stdout."""
    response = await handle_message(message)
    print(response)


async def main() -> None:
    """Main entry point."""
    args = parse_args()

    if args.test:
        # Test mode: handle message and exit
        await handle_test_message(args.test)
        sys.exit(0)

    # Telegram mode: start the bot (implemented in Task 2)
    print("Telegram mode not yet implemented. Use --test for testing.")
    sys.exit(0)


if __name__ == "__main__":
    asyncio.run(main())
