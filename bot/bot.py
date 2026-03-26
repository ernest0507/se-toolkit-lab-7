"""Telegram bot launcher with support for test mode."""

import argparse
import asyncio
import sys

from handlers.commands import handle_message


def build_parser() -> argparse.ArgumentParser:
    """Create argument parser."""
    parser = argparse.ArgumentParser(description="LMS Telegram Bot")
    parser.add_argument(
        "--test",
        type=str,
        help="Pass a message to run in test mode (e.g. '/start')"
    )
    return parser


async def main() -> None:
    """Main execution function."""
    parser = build_parser()
    args = parser.parse_args()

    # If test mode is enabled
    if args.test:
        reply = await handle_message(args.test)
        print(reply)
        return

    # Default mode (not implemented yet)
    print("Telegram mode not implemented. Use --test argument.")
    return


def entrypoint() -> None:
    """Synchronous entrypoint wrapper."""
    asyncio.run(main())
    sys.exit(0)


if __name__ == "__main__":
    entrypoint()
