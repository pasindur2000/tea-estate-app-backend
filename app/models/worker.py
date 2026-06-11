"""
models/worker.py
----------------
Pydantic schemas for the Workers collection.
"""

from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import date
from app.models.base import TimestampMixin


# ── Create ───────────────────────────────────────────────────────────────────
class WorkerCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, example="Kamal")
    nic: str = Field(..., min_length=9, max_length=12, example="981234567V")
    phone: str = Field(..., min_length=10, max_length=15, example="0771234567")
    estateId: str
    joinedDate: date = Field(..., example="2026-05-01")
    status: Literal["active", "inactive"] = "active"


# ── Update ───────────────────────────────────────────────────────────────────
class WorkerUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    phone: Optional[str] = Field(None, min_length=10, max_length=15)
    status: Optional[Literal["active", "inactive"]] = None


# ── Response ─────────────────────────────────────────────────────────────────
class WorkerResponse(TimestampMixin):
    workerId: str
    estateId: str
    name: str
    nic: str
    phone: str
    status: str
    joinedDate: str
    createdBy: str
