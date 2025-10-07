"""
LeetCode Agent - A Python package for solving LeetCode problems using AI agents.

This package provides tools and utilities for automating LeetCode problem solving
using language models and web automation.
"""

__version__ = "0.1.0"
__author__ = "LeetCode Agent Developer"
__email__ = "developer@example.com"

# Import main components for easy access
from .core import LeetCodeAgent
from .browser import PlaywrightManager, init_playwright, cleanup_playwright
from .utils import setup_logging, get_config, validate_url
from .main import main

__all__ = [
    "LeetCodeAgent",
    "PlaywrightManager",
    "init_playwright",
    "cleanup_playwright",
    "setup_logging",
    "get_config", 
    "validate_url",
    "main",
]
