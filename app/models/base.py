"""
models/base.py
--------------
Shared base classes and helper types used across all models.
"""

from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional


class TimestampMixin(BaseModel):
    """Adds createdAt / updatedAt to any model that inherits it."""
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None


class StatusEnum:
    ACTIVE = "active"
    INACTIVE = "inactive"
