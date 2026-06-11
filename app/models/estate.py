"""
models/estate.py
----------------
Pydantic schemas for the Estates collection.

We have THREE kinds of schema for every resource:
  - Create  → what the client SENDS when creating
  - Update  → what the client SENDS when editing (all fields optional)
  - Response → what the API RETURNS (includes server-set fields)
"""

from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime
from app.models.base import TimestampMixin


# ── Create ───────────────────────────────────────────────────────────────────
class EstateCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, example="Green Valley Tea Estate")
    location: str = Field(..., min_length=2, max_length=200, example="Kandy")
    status: Literal["active", "inactive"] = "active"


# ── Update ───────────────────────────────────────────────────────────────────
class EstateUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    location: Optional[str] = Field(None, min_length=2, max_length=200)
    status: Optional[Literal["active", "inactive"]] = None


# ── Response ─────────────────────────────────────────────────────────────────
class EstateResponse(TimestampMixin):
    estateId: str
    name: str
    location: str
    status: str
