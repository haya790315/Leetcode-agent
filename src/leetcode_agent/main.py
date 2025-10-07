"""
Main entry point for the LeetCode Agent package.

This module provides the main function that can be called when
running the package as a module: python -m leetcode_agent
"""

import argparse
import os
import sys

from leetcode_agent.core import LeetCodeAgent
from leetcode_agent.utils import setup_logging
from leetcode_agent.agent import AiAgent, ConversationTemplate


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

    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Start interactive AI chat mode (no browser automation)",
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

    # Check if interactive mode is requested
    if parsed_args.interactive:
        return interactive_mode()

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


def interactive_mode():
    """
    Entry point for interactive mode command.

    This function provides the interactive AI chat functionality
    without the full LeetCode automation workflow.
    """
    import time

    print("🤖 LeetCode AI Agent - Interactive Mode")
    print("=" * 50)
    print("📝 You can paste LeetCode problems or ask for help")
    print("💡 Type 'quit', 'exit', or 'q' to end the session")
    print("=" * 50)

    try:
        # Initialize the AI agent directly
        agent = AiAgent(
            model_name="gemini-2.5-flash",
            temperature=0.5,
            api_key=os.getenv("GOOGLE_API_KEY"),
            template=ConversationTemplate(),
        )

        print("✅ AI Agent initialized successfully!")
        print()

        # Interactive loop
        while True:
            try:
                # Get user input
                user_input = input("🧑 You: ").strip()

                # Check for quit commands
                if user_input.lower() in ["quit", "exit", "q", ""]:
                    break

                # Send message to agent
                print("🤖 AI Agent: ", end="", flush=True)
                response = agent.chat(user_input)
                print(response)
                print()

            except KeyboardInterrupt:
                print("\n\n👋 Session interrupted by user")
                break
            except EOFError:
                print("\n\n👋 Session ended")
                break

        # Show summary when quitting
        print("\n" + "=" * 50)
        print("📊 Session Summary:")
        print("=" * 50)
        summary = agent.get_conversation_summary()
        for key, value in summary.items():
            print(f"{key}: {value}")
        print("=" * 50)
        print("👋 Thank you for using LeetCode AI Agent Interactive Mode!")

    except Exception as e:
        print(f"❌ Error initializing agent: {e}")
        print("💡 Make sure you have set the GOOGLE_API_KEY environment variable")
        return 1

    return 0


if __name__ == "__main__":
    interactive_mode()
