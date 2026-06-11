"""
models/user.py
--------------
Pydantic schemas for the Users collection.
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Literal
from app.models.base import TimestampMixin


# ── Create ───────────────────────────────────────────────────────────────────
class UserCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, example="Saman")
    email: EmailStr
    password: str = Field(..., min_length=6)        # used to create Firebase Auth account
    role: Literal["director", "supervisor"] = "supervisor"
    estateId: str


# ── Update ───────────────────────────────────────────────────────────────────
class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    status: Optional[Literal["active", "inactive"]] = None


# ── Response ─────────────────────────────────────────────────────────────────
class UserResponse(TimestampMixin):
    uid: str
    name: str
    email: str
    role: str
    estateId: str
    status: str
