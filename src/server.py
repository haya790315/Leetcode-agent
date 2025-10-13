from mcp.server.fastmcp import FastMCP
from leetcode_agent import *

# Initialize the FastMCP server for Leetcode automation
mcp = FastMCP("Leetcode MCP", "0.1.0")

# Global variable to store the browser session (playwright, context, page)
browser_manager = None

# Message to return when no browser session is active
no_browser_session_message = "No browser session found. Please open the browser and access leetcode.com for the user first."


@mcp.tool()
async def access_leetcode_web():
    """
    Launch a new Chrome browser and navigate to leetcode.com.
    Sets some local storage items for the user session.
    Returns a message indicating whether the user is logged in.
    """
    global browser_manager
    browser_manager = await init_playwright(headless=False)
    _, _, page = browser_manager
    await page.goto("https://leetcode.com")
    local_storage_items = {
        "hasShownNewFeatureGuide": "true",
        "global_lang": "java",
    }

    # Set local storage items for the session
    for key, value in local_storage_items.items():
        if value:
            await page.evaluate(f"localStorage.setItem('{key}', '{value}')")

    cookies = await page.context.cookies()
    leetcode_session = next(
        (c for c in cookies if c["name"] == "LEETCODE_SESSION"), None
    )
    if leetcode_session:
        # User is logged in
        return "Browser opened and user login already."
    else:
        # User is not logged in
        return (
            "User not logged in yet. Ask the user if they would like to login now, "
            "and if yes, navigate to the login page."
        )


@mcp.tool()
async def goto_url(url: str):
    """
    Navigate the browser to a specified URL.

    Args:
        url (str): The URL to navigate to.

    Returns:
        str: Status message after navigation.
    """
    global browser_manager
    if not browser_manager:
        return no_browser_session_message
    _, _, page = browser_manager
    await page.goto(url)
    return f"Navigated to {url}"


@mcp.tool()
async def go_to_daily_problem():
    """
    Navigate the browser to the LeetCode daily problem page.
    Returns a status message after navigation.
    """

    global browser_manager
    if not browser_manager:
        return no_browser_session_message
    _, _, page = browser_manager
    agent = LeetCodeAgent(
        headless=False, log_level="INFO", lang="java", browser_manager=browser_manager
    )
    await agent.navigate_to_daily_problem(page)
    return "Navigated to daily problem."


@mcp.tool()
async def get_problem_description() -> str:
    """
    Get the problem description from the current LeetCode problem page.
    Returns a prompt for the user to decide whether to solve the problem.
    """
    global browser_manager
    if not browser_manager:
        return no_browser_session_message
    _, _, page = browser_manager
    agent = LeetCodeAgent(
        headless=False, log_level="INFO", lang="java", browser_manager=browser_manager
    )
    problem_description = await agent.grabProblem(page)
    return (
        f"The problem description is: {problem_description}\n"
        "Ask the user if they want me to solve it. "
        "If yes, solve the problem and write the code in the code editor on the page."
    )


@mcp.tool()
async def write_solution_code(code: str) -> str:
    """
    Write the solution code to the code editor on the page.

    Args:
        code (str): The solution code to write. It should not contain any code block markdown syntax.

    Returns:
        str: Status message after writing the code.
    """
    global browser_manager
    if not browser_manager:
        return no_browser_session_message
    _, _, page = browser_manager
    agent = LeetCodeAgent(
        headless=False, log_level="INFO", lang="java", browser_manager=browser_manager
    )
    await agent.writeAnswer(page, code, autoSubmit=False)
    return "The solution code has been written to the code editor on the page. Please check it."


@mcp.tool()
async def close_browser():
    """
    Close the browser session and clean up resources.
    Returns a status message after closing the browser.
    """
    global browser_manager
    if not browser_manager:
        return "Browser has already been closed."
    playwright, context, page = browser_manager
    await cleanup_playwright(playwright, context, page)
    browser_manager = None
    return "Browser closed."


if __name__ == "__main__":
    print("Starting MCP server...")
    # Start the MCP server using stdio transport
    mcp.run(transport="stdio")
