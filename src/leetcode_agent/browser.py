"""
Browser automation module for LeetCode Agent.

This module provides web automation capabilities using Playwright,
with proper resource management and error handling.
"""

from leetcode_agent.utils import setup_logging
from playwright.sync_api import sync_playwright
import os
from dotenv import load_dotenv
from playwright.sync_api._generated import Browser, BrowserContext, Page, Playwright

load_dotenv()


def init_playwright(
    lang,
    headless,
) -> tuple[Playwright, Browser, BrowserContext, Page]:
    """
    Initialize Playwright and return browser resources.

    Args:
        url (str, optional): The URL to navigate to.
                          Defaults to LEETCODE_URL from .env or https://leetcode.com/problemset/
        headless (bool, optional): Whether to run in headless mode.
                                Defaults to value from .env or True

    Returns:
        tuple: (playwright, browser, context, page)

    Note: Remember to call cleanup_playwright() when done to close resources!
    """
    if headless is None:
        headless = os.getenv("HEADLESS_BROWSER", "True").lower() == "true"

    # Don't use 'with' here since we want to return active objects
    playwright = sync_playwright().start()

    # Launch browser with stealth settings
    browser = playwright.chromium.launch(
        headless=headless,
        channel="chrome",  # This uses real Chrome instead of Chromium
    )

    # Create context with realistic user agent and settings
    context = browser.new_context(
        viewport={"width": 1920, "height": 900},  # Common resolution
    )

    # add LeetCode session cookie for authentication
    context.add_cookies(
        [
            {
                "name": "LEETCODE_SESSION",
                "value": os.getenv("LEETCODE_SESSION"),
                "domain": ".leetcode.com",
                "path": "/",
            }
        ]
    )

    page = context.new_page()
    page.goto("https://leetcode.com")

    # Add local storage values after navigation
    local_storage_items = {
        "hasShownNewFeatureGuide": "true",
        "global_lang": lang,
    }

    # Set local storage items
    for key, value in local_storage_items.items():
        if value:  # Only set if value exists
            page.evaluate(f"localStorage.setItem('{key}', '{value}')")

    return playwright, browser, context, page


def cleanup_playwright(playwright, browser, context=None, page=None):
    """
    Properly cleanup Playwright resources.

    Args:
        playwright: Playwright instance
        browser: Browser instance
        context: Browser context (optional)
        page: Page instance (optional)
    """
    try:
        if page:
            page.close()
        if context:
            context.close()
        if browser:
            browser.close()
        if playwright:
            playwright.stop()
    except Exception as e:
        print(f"Error during cleanup: {e}")


class PlaywrightManager:
    """
    Context manager for Playwright that handles cleanup automatically.

    This implements the Context Manager Protocol (__enter__ and __exit__).
    It ensures that browser resources are always properly cleaned up,
    even if an exception occurs during execution.

    Usage:
        with PlaywrightManager("https://example.com") as (playwright, browser, context, page):
            # Use page here - this is where you do your actual work
            page.click("button")
            title = page.title()
            page.screenshot(path="screenshot.png")
        # Everything is automatically cleaned up here

    Benefits:
        - No memory leaks from unclosed browsers
        - No zombie browser processes
        - Exception-safe resource management
        - Cleaner, more readable code
    """

    def __init__(self, lang, headless):
        """
        Initialize the manager with URL and browser settings.

        Args:
            url (str): The URL to navigate to when page is created
            headless (bool, optional): Whether to run browser in headless mode
        """
        self.headless = headless
        self.resources = None  # Will store (playwright, browser, context, page)
        self.lang = lang
        self.logger = setup_logging("INFO")

    def __enter__(self):
        """
        Called when entering the 'with' block.

        This method:
        1. Creates the browser (heavy operation)
        2. Creates a context (like an incognito window)

        Returns:
            tuple: (playwright, browser, context, page) for use in the with block
        """
        self.resources = init_playwright(
            self.lang,
            self.headless,
        )
        return self.resources

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Called when exiting the 'with' block (even on exceptions).

        This method:
        1. Closes the page (tab)
        2. Closes the context (window)
        3. Closes the browser (application)
        4. Stops the playwright instance

        Args:
            exc_type: Exception type (if any exception occurred)
            exc_val: Exception value (if any exception occurred)
            exc_tb: Exception traceback (if any exception occurred)

        Returns:
            None: (returning None means "don't suppress exceptions")
        """
        if self.resources:
            self.logger.info("🧹 Cleaning up browser resources...")
            cleanup_playwright(*self.resources)
            self.logger.info("✅ Cleanup completed")

        # If an exception occurred, don't suppress it (return None/False)
        if exc_type is not None:
            self.logger.error(
                f"⚠️  Exception occurred during execution: {exc_type.__name__}: {exc_val}"
            )

        return False  # Don't suppress exceptions
