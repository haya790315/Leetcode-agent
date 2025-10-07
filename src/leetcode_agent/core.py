"""
Core LeetCode Agent functionality.

This module contains the main agent class and problem-solving logic.
"""

from typing import Dict, Any
from xmlrpc.client import boolean

from .agent import ConversationTemplate, AiAgent
from .browser import PlaywrightManager
from .utils import setup_logging
import time
import os
import platform
from dotenv import load_dotenv
from playwright.sync_api._generated import Page

load_dotenv()


class LeetCodeAgent:
    """
    Main LeetCode Agent class for automated problem solving.

    This class coordinates between browser automation, AI models,
    and problem-solving strategies.
    """

    def __init__(self, headless: bool, log_level: str, lang: str):
        """
        Initialize the LeetCode Agent.

        Args:
            headless (bool): Whether to run browser in headless mode
            log_level (str): Logging level (DEBUG, INFO, WARNING, ERROR)
            lang (str): Programming language for solving problems
        """
        self.headless = headless
        self.logger = setup_logging(log_level)
        self.browser_manager = None
        self.lang = lang

        # State variables to store current problem and editor content
        self.current_problem_text = None
        self.current_editor_text = None
        self.wrong_case = []

        # Detect OS for cross-platform keyboard shortcuts
        self.is_mac = platform.system() == "Darwin"

        # AI agent model
        self.ai_agent = None  # Placeholder for AI agent instance

    def start(self, url) -> None:
        """
        Start the agent and initialize browser.

        Args:
            url (str): URL to navigate to
        """
        self.logger.info(f"🚀 Starting LeetCode Agent...")
        self.logger.info(f"🌐 Navigating to: {url}")
        self.browser_manager = PlaywrightManager(self.lang, headless=self.headless)
        self.ai_agent = AiAgent(
            model_name="gemini-2.5-flash",
            temperature=0.5,
            api_key=os.getenv("GOOGLE_API_KEY"),
            template=ConversationTemplate(),
        )  # Initialize your AI agent here

        with self.browser_manager as (playwright, browser, context, page):
            if not url:
                self.logger.info(f"🚀 Starting browser and navigating to daily problem")
                self.navigate_to_daily_problem(page)
            else:
                self.logger.info(f"🚀 Starting browser and navigating to {url}")
                page.goto(url)

            self.grabProblem(page)
            attempt = 0

            while attempt < 10:
                self.logger.info(f"🧠 Attempt {attempt + 1}: Solving problem...")

                result_code = self.solve_problem(attempt)
                self.writeAnswer(page, result_code)
                if self.grab_result(page):
                    self.logger.info("🎉 Problem solved successfully!")
                    self.logger.info("📝 Writing solution to file...")
                    self.ai_agent.chat(
                        """Great! The solution worked perfectly. Thank you! There still has some work to do 
                          - please create a markdown file and name it with the problem title in the solutions folder.
                          - it should include some sections:
                            1. Problem Description: A brief overview of the problem.
                            2. Solution Approach: A detailed explanation of the approach taken to solve the problem.
                            3. Code Implementation: The final code solution.
                            4. Complexity Analysis: Time and space complexity of the solution.
                          you can ask for some tools to help you with this task.
                        """
                    )
                    break
                attempt += 1

            self.logger.info("📊 Conversation Summary:")
            summary = self.ai_agent.get_conversation_summary()
            for key, value in summary.items():
                self.logger.info(f"  {key}: {value}")

            time.sleep(20)

    def navigate_to_daily_problem(self, page: Page) -> None:
        """
        Navigate to LeetCode's daily coding challenge problem page.

        Args:
            page (Page): Playwright page instance
        """
        if not self.browser_manager:
            raise RuntimeError("Agent not started. Call start() first.")

        # Use the context manager properly
        # Navigate to problem page
        page.goto("https://leetcode.com/problemset/")

        # First, let's log the target element's HTML for debugging
        daily_problem_link = "xpath=//a[contains(@class,'group flex flex-col rounded-[8px] duration-300 bg-fill-quaternary dark:bg-fill-quaternary')]"

        page.locator(daily_problem_link).first.click()

        page.wait_for_load_state("networkidle")

    def grabProblem(self, page: Page) -> str:
        """
        Extract problem description and editor content from LeetCode page.
        """

        # Get current editor content
        editor = page.locator(".view-lines").first
        editor.click()

        # Save editor text to state
        self.editor_text = editor.inner_text()

        problemElement = page.locator(
            "xpath=//div[contains(@class, 'flex w-full flex-1 flex-col gap-4 overflow-y-auto px-4 py-5')]"
        )

        problem_text = problemElement.inner_text()

        # Save problem text to state
        self.problem_text = problem_text

        # self.logger.info(f"📝 Problem text preview:\n{problem_text[:500]}...")
        return problem_text

    def grab_result(self, page: Page) -> boolean:
        """
        Check submission result and determine if the solution was accepted.

        Args:
            page (Page): Playwright page instance

        Returns:
            boolean: True if solution was accepted, False otherwise
        """
        page.wait_for_timeout(10000)
        result_area = "xpath=//*[@data-layout-path='/ts0/tb1']"
        result_text = page.locator(result_area).inner_text()

        if "Accepted" in result_text:
            self.logger.info("✅ Answer Accepted")
            return True

        self.wrong_case.append(result_text)
        self.logger.info("❌ Answer not accepted")
        return False

    def solve_problem(self, attempt: int) -> str:
        """
        Solve a specific LeetCode problem.

        Args:
            attempt (int): Number of iterations attempted
        Returns:
            str: The solution code generated by the AI agent
        """
        if attempt > 0:
            result = self.ai_agent.chat(
                f"""
                  the provided code did not work. Please fix it.
                  and the wrong case is:
                  {self.wrong_case[-1]}
                  please try again.
              """
            )
        else:
            result = self.ai_agent.chat(
                f"""
                Here is the problem description:
                {self.problem_text}

                and the template of the code is:
                {self.editor_text}

                and the wrong case is:
                {self.wrong_case[-1] if self.wrong_case else 'No wrong case provided'}

                Please analyze the language of the code and return the same language of the code.
                Return ONLY the complete working code without any markdown formatting, explanations, or comments.
                """
            )
        return result

    def writeAnswer(self, page: Page, result_code: str) -> None:
        """
        Write and submit the generated solution code to LeetCode.

        Args:
            page (Page): Playwright page instance
            result_code (str): The solution code to submit
        """

        editor = page.locator(".view-lines").first
        editor.click()

        # Code to paste
        code = f"""{result_code}"""

        # Use JSON.stringify for safer string handling
        page.evaluate(
            f"""
        async () => {{
            const code = {repr(code)};
            await navigator.clipboard.writeText(code);
        }}
        """
        )

        # Select all existing content
        if self.is_mac:
            select_all_key = "Meta+a"
            paste_key = "Meta+v"
        else:
            select_all_key = "Control+a"
            paste_key = "Control+v"

        page.keyboard.press(select_all_key)
        page.keyboard.press("Delete")

        # Paste the code
        page.keyboard.press(paste_key)

        self.logger.info("✅ Code pasted successfully")

        page.click("xpath=//button[@data-cid='3']")

        self.logger.info("📤 Answer submitted.")

    def get_problem(self) -> Dict[str, Any]:
        """
        Get the current state of problem and editor content.

        Returns:
            Dict containing current problem text, editor text, and metadata
        """
        return {
            "problem_text": self.problem_text,
            "editor_text": self.editor_text,
            "wrong_case": self.wrong_case,
        }

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with cleanup."""
        if self.browser_manager:
            # The browser manager will handle its own cleanup
            pass
