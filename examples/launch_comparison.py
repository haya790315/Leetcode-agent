"""
Comparison: Regular vs Persistent Browser Launch
Demonstrates the difference between browser launch methods
"""

from pathlib import Path
from playwright.sync_api import sync_playwright


def regular_browser_launch():
    """Traditional way - browser + context separately"""
    with sync_playwright() as p:
        # Step 1: Launch browser
        browser = p.chromium.launch(headless=False)

        # Step 2: Create context (temporary, no data saved)
        context = browser.new_context()

        # Step 3: Create page
        page = context.new_page()

        # ❌ When browser closes, ALL DATA IS LOST
        # ❌ No cookies, login sessions, or settings saved
        # ❌ Next run starts completely fresh

        page.goto("https://leetcode.com")
        input("Press Enter to close...")

        browser.close()  # Everything lost!


def persistent_context_launch():
    """Modern way - persistent context with data storage"""
    with sync_playwright() as p:
        profile_dir = Path.home() / ".leetcode_agent" / "browser_profile"
        profile_dir.mkdir(parents=True, exist_ok=True)

        # Single step: Launch browser WITH persistent data storage
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(profile_dir),  # 🔑 Key difference!
            channel="chrome",  # Use installed Chrome
            headless=False,
            bypass_csp=True,  # Bypass Content Security Policy (CSP)
        )

        # Browser already has a context with saved data
        page = context.pages[0] if context.pages else context.new_page()

        # ✅ Cookies, login sessions, settings PRESERVED
        # ✅ Next run continues where you left off
        # ✅ Acts like a real browser profile

        page.goto("https://leetcode.com")
        input("Press Enter to close...")

        context.close()  # Data is SAVED to user_data_dir!


if __name__ == "__main__":
    print("Choose launch method:")
    print("1. Regular launch (temporary)")
    print("2. Persistent context (saves data)")

    choice = input("Enter choice: ")

    if choice == "1":
        regular_browser_launch()
    else:
        persistent_context_launch()
