"""
utils/response.py
-----------------
A single helper that wraps every API response in a consistent shape.

Every endpoint in this API returns:
{
    "success": true | false,
    "message": "Human-readable result",
    "data": { ... }   ← the actual payload
}

This makes it very easy for the mobile app to handle responses uniformly.
"""

from typing import Any, Optional


def success_response(message: str, data: Any = None) -> dict:
    return {
        "success": True,
        "message": message,
        "data": data,
    }


def error_response(message: str, data: Any = None) -> dict:
    return {
        "success": False,
        "message": message,
        "data": data,
    }
