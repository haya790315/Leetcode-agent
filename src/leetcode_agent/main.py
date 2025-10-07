"""
Main entry point for the LeetCode Agent package.

This module provides the main function that can be called when
running the package as a module: python -m leetcode_agent
"""

import argparse
import sys
import time
from .core import LeetCodeAgent
from .utils import setup_logging


def create_parser():
    """Create command line argument parser."""
    parser = argparse.ArgumentParser(
        description="LeetCode Agent - Automated problem solving assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m leetcode_agent                    # Start with default settings
  python -m leetcode_agent --headless        # Run in headless mode
  python -m leetcode_agent --log-level DEBUG # Enable debug logging
  python -m leetcode_agent --lang java       # Set default programming language to Java
        """,
    )

    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run browser in headless mode (no GUI)",
    )

    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Set logging level (default: INFO)",
    )

    parser.add_argument(
        "--lang",
        choices=[
            "java",
            "python3",
            "python",
            "javascript",
            "typescript",
            "csharp",
            "c",
            "golang",
            "kotlin",
            "swift",
            "rust",
            "ruby",
            "php",
            "dart",
            "scala",
            "elixir",
            "erlang",
            "racket",
        ],
        default="java",
        help="Set programming language (default: java)",
    )

    parser.add_argument(
        "--url",
        type=str,
        help="LeetCode base URL (default: https://leetcode.com)",
    )

    return parser


def main(args=None):
    """
    Main entry point for the LeetCode Agent.

    Args:
        args: Command line arguments (optional, for testing)
    """
    parser = create_parser()
    parsed_args = parser.parse_args(args)

    # Set up logging
    logger = setup_logging(parsed_args.log_level)

    try:
        # Initialize the agent
        agent = LeetCodeAgent(
            headless=parsed_args.headless,
            log_level=parsed_args.log_level,
            lang=parsed_args.lang,
        )

        # Start the agent
        agent.start(parsed_args.url)

    except KeyboardInterrupt:
        logger.info("\n🛑 Agent interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Error running agent: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
