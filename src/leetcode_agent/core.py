"""
Core LeetCode Agent functionality.

This module contains the main LeetCodeAgent class and problem-solving logic for automating LeetCode tasks.
"""

import asyncio
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

    This class coordinates browser automation, AI models, and problem-solving strategies.
    """

    def __init__(self, headless: bool, log_level: str, lang: str, browser_manager=None):
        """
        Initialize the LeetCode Agent.

        Args:
            headless (bool): Whether to run the browser in headless mode.
            log_level (str): Logging level (DEBUG, INFO, WARNING, ERROR).
            lang (str): Programming language for solving problems.
            browser_manager: Optional browser manager instance.
        """
        self.headless = headless
        self.logger = setup_logging(log_level)
        self.browser_manager = browser_manager
        self.lang = lang

        # State variables to store current problem and editor content
        self.current_problem_text = None  # Current problem statement text
        self.current_editor_text = None  # Current code in the editor
        self.wrong_case = []  # List of wrong test cases

        # Detect OS for cross-platform keyboard shortcuts
        self.is_mac = platform.system() == "Darwin"

        # AI agent model (to be initialized later)
        self.ai_agent = None

    async def start(self, url) -> None:
        """
        Start the agent and initialize the browser.

        Args:
            url (str): URL to navigate to.
        """
        self.logger.info(f"🚀 Starting LeetCode Agent...")
        self.browser_manager = PlaywrightManager(headless=self.headless)
        self.ai_agent = AiAgent(
            model_name="gemini-2.5-flash",
            temperature=0.5,
            api_key=os.getenv("GOOGLE_API_KEY"),
            template=ConversationTemplate(),
        )  # Initialize your AI agent here

        async with self.browser_manager as (playwright, context, page):
            input("Please complete login, then press Enter here to continue...")
            # Add local storage values before navigation
            local_storage_items = {
                "hasShownNewFeatureGuide": "true",
                "global_lang": self.lang,
            }

            # Set local storage items
            for key, value in local_storage_items.items():
                if value:
                    await page.evaluate(f"localStorage.setItem('{key}', '{value}')")

            if not url:
                self.logger.info(f"🚀 Starting browser and navigating to daily problem")
                await self.navigate_to_daily_problem(page)
            else:
                self.logger.info(f"🚀 Starting browser and navigating to {url}")
                await page.goto(url)

            await self.grabProblem(page)
            attempt = 0
            while attempt < 5:
                self.logger.info(f"🧠 Attempt {attempt + 1}: Solving problem...")

                result_code = self.solve_problem(attempt)
                await self.writeAnswer(page, result_code)
                if await self.grab_result(page):
                    self.logger.info("🎉 Problem solved successfully!")
                    self.logger.info("📝 Writing solution to file...")
                    self.ai_agent.chat(
                        """Great! The solution worked perfectly. Thank you! There still has some work to do
                          - please create a markdown file and name it with the problem title and difficulty like `1. Two Sum - (Easy).md` in the solutions folder.
                          - it should include some sections:
                            1. Problem Explanation: A brief overview of the problem.
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

            await asyncio.sleep(20)

    async def navigate_to_daily_problem(self, page: Page) -> None:
        """
        Navigate to LeetCode's daily coding challenge problem page.

        Args:
            page (Page): Playwright page instance.
        """
        if not self.browser_manager:
            raise RuntimeError("Agent not started. Call start() first.")

        # Use the context manager properly
        # Navigate to problem page
        await page.goto("https://leetcode.com/problemset/")

        # First, let's log the target element's HTML for debugging
        daily_problem_link = "xpath=//a[contains(@class,'group flex flex-col rounded-[8px] duration-300 bg-fill-quaternary dark:bg-fill-quaternary')]"

        await page.locator(daily_problem_link).first.click()

        await page.wait_for_load_state("networkidle")

    async def grabProblem(self, page: Page) -> str:
        """
        Extract problem description and editor content from LeetCode page.

        Args:
            page (Page): Playwright page instance.

        Returns:
            str: The problem description text.
        """

        # Get current editor content

        editor = page.locator(".view-lines").first
        await editor.click()

        # Save editor text to state
        self.editor_text = await editor.inner_text()

        problemElement = page.locator(
            "xpath=//div[contains(@class, 'flex w-full flex-1 flex-col gap-4 overflow-y-auto px-4 py-5')]"
        )

        problem_text = await problemElement.inner_text()

        # Save problem text to state
        self.problem_text = problem_text

        # self.logger.info(f"📝 Problem text preview:\n{problem_text[:500]}...")
        return problem_text

    async def grab_result(self, page: Page) -> boolean:
        """
        Check submission result and determine if the solution was accepted.

        Args:
            page (Page): Playwright page instance.

        Returns:
            boolean: True if solution was accepted, False otherwise.
        """
        await page.wait_for_timeout(10000)
        result_area = "xpath=//*[@data-layout-path='/ts0/tb1']"
        result_text = await page.locator(result_area).inner_text()

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
            attempt (int): Number of iterations attempted.

        Returns:
            str: The solution code generated by the AI agent.
        """
        if attempt > 0:
            result = self.ai_agent.chat(
                f"""
                  the provided code did not work. Please fix it.
                  and the wrong case is:
                  {self.wrong_case[-1]}
                  please try again.
                  Return ONLY the code without any code block like ```java or ```python, and without any explanations, or comments.
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
                Return ONLY the code without any code block like ```java or ```python, and without any explanations, or comments.
                """
            )
        return result

    async def writeAnswer(
        self, page: Page, result_code: str, autoSubmit: bool = True
    ) -> None:
        """
        Write and submit the generated solution code to LeetCode.

        Args:
            page (Page): Playwright page instance.
            result_code (str): The solution code to submit.
            autoSubmit (bool): Whether to automatically submit the answer after writing. Default is True.
        """

        editor = page.locator(".view-lines").first
        await editor.click()

        # Code to paste
        code = f"""{result_code}"""

        # Use JSON.stringify for safer string handling
        await page.evaluate(
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

        await page.keyboard.press(select_all_key)
        await page.keyboard.press("Delete")

        # Paste the code
        await page.keyboard.press(paste_key)

        self.logger.info("✅ Code pasted successfully")

        if autoSubmit:
            await page.click("xpath=//button[@data-cid='3']")
            self.logger.info("📤 Answer submitted.")

    def get_problem(self) -> Dict[str, Any]:
        """
        Get the current state of problem and editor content.

        Returns:
            Dict[str, Any]: Dictionary containing current problem text, editor text, and metadata.
        """
        return {
            "problem_text": self.problem_text,
            "editor_text": self.editor_text,
            "wrong_case": self.wrong_case,
        }

    def __enter__(self):
        """
        Context manager entry.
        Returns:
            self: The LeetCodeAgent instance.
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Context manager exit with cleanup.
        Args:
            exc_type: Exception type.
            exc_val: Exception value.
            exc_tb: Exception traceback.
        """
        if self.browser_manager:
            # The browser manager will handle its own cleanup
            pass
