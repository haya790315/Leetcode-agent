"""
Browser automation module for LeetCode Agent (async version).
This module provides web automation capabilities using Playwright async API,
with proper resource management and error handling.
"""

from leetcode_agent.utils import setup_logging
import os
from dotenv import load_dotenv
from playwright.async_api import async_playwright, Playwright, BrowserContext, Page

load_dotenv()


async def init_playwright(
    headless,
) -> tuple[Playwright, BrowserContext, Page]:
    """
    Initialize Playwright and return browser resources (async version).

    Args:
        url (str, optional): The URL to navigate to.
                          Defaults to LEETCODE_URL from .env or https://leetcode.com/login/
        headless (bool, optional): Whether to run in headless mode.
                                Defaults to value from .env or True

    Returns:
        tuple: (playwright, context, page)

    Note: Remember to call cleanup_playwright() when done to close resources!
    """
    if headless is None:
        headless = os.getenv("HEADLESS_BROWSER", "True").lower() == "true"

    playwright = await async_playwright().start()
    context = await playwright.chromium.launch_persistent_context(
        "",
        headless=headless,
        channel="chrome",  # This uses real Chrome instead of Chromium
        args=[
            "--disable-blink-features=AutomationControlled",  # Stealth
        ],
        viewport={"width": 1280, "height": 900},
    )

    pages = context.pages
    page = pages[0] if pages else await context.new_page()
    await page.goto("https://leetcode.com/accounts/login", wait_until="load")

    return playwright, context, page


async def cleanup_playwright(playwright, context=None, page=None):
    """
    Properly cleanup Playwright resources.

    Args:
        playwright: Playwright instance
        context: Browser context (optional)
        page: Page instance (optional)
    """
    try:
        if page:
            await page.close()
        if context:
            await context.close()
        if playwright:
            await playwright.stop()
    except Exception as e:
        print(f"Error during cleanup: {e}")


class PlaywrightManager:
    """
    Async context manager for Playwright that handles cleanup automatically.

    Usage:
        async with AsyncPlaywrightManager(headless) as (playwright, context, page):
            # Use page here - this is where you do your actual work
            await page.click("button")
            title = await page.title()
            await page.screenshot(path="screenshot.png")
        # Everything is automatically cleaned up here
    """

    def __init__(self, headless):
        self.headless = headless
        self.resources = None  # Will store (playwright, context, page)
        self.logger = setup_logging("INFO")

    async def __aenter__(self):
        self.resources = await init_playwright(self.headless)
        return self.resources

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.resources:
            self.logger.info("🧹 Cleaning up browser resources...")
            await cleanup_playwright(*self.resources)
            self.logger.info("✅ Cleanup completed")
        if exc_type is not None:
            self.logger.error(
                f"⚠️  Exception occurred during execution: {exc_type.__name__}: {exc_val}"
            )
        return False
