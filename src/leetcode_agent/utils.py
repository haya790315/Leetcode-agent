"""
Utility functions for LeetCode Agent.

This module provides common utilities like logging setup,
configuration management, and helper functions.
"""

import logging
import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


def setup_logging(level: str = "INFO") -> logging.Logger:
    """
    Set up logging configuration for the application.
    
    Args:
        level (str): Logging level (DEBUG, INFO, WARNING, ERROR)
        
    Returns:
        Configured logger instance
    """
    # Convert string level to logging constant
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    
    # Create logger
    logger = logging.getLogger("leetcode_agent")
    logger.setLevel(numeric_level)
    
    # Remove existing handlers to avoid duplicates
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(console_handler)
    
    return logger


def get_config(key: str, default: Optional[str] = None) -> Optional[str]:
    """
    Get configuration value from environment variables.
    
    Args:
        key (str): Configuration key
        default (Optional[str]): Default value if key not found
        
    Returns:
        Configuration value or default
    """
    return os.getenv(key, default)


def validate_url(url: str) -> bool:
    """
    Validate if a URL is a valid LeetCode URL.
    
    Args:
        url (str): URL to validate
        
    Returns:
        True if valid, False otherwise
    """
    valid_domains = [
        "leetcode.com",
        "leetcode.cn",
        "leetcode-cn.com"
    ]
    
    return any(domain in url.lower() for domain in valid_domains)


def format_problem_url(problem_slug: str) -> str:
    """
    Format a problem slug into a full LeetCode URL.
    
    Args:
        problem_slug (str): Problem slug (e.g., "two-sum")
        
    Returns:
        Full problem URL
    """
    base_url = get_config("LEETCODE_URL", "https://leetcode.com")
    return f"{base_url}/problems/{problem_slug}/"


def safe_filename(title: str) -> str:
    """
    Convert a problem title to a safe filename.
    
    Args:
        title (str): Problem title
        
    Returns:
        Safe filename string
    """
    # Remove special characters and replace spaces with underscores
    import re
    safe_title = re.sub(r'[^\w\s-]', '', title)
    safe_title = re.sub(r'[\s_-]+', '_', safe_title)
    return safe_title.lower().strip('_')
