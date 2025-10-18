"""
Core utility functions for the MCP server application
"""
import re


def validate_name(name: str) -> bool:
    """
    Validates that a string contains only alphanumerics and underscore,
    with at least one alphabetic character.

    Args:
        name (str): The string to validate

    Returns:
        bool: True if valid, False otherwise
    """
    if not name or not isinstance(name, str):
        return False

    # Check if contains only alphanumerics and underscore
    if not re.match(r'^[a-zA-Z0-9_]+$', name):
        return False

    # Check if contains at least one alphabetic character
    if not re.search(r'[a-zA-Z]', name):
        return False

    return True