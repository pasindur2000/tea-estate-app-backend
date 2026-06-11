"""
models/tea_entry.py
-------------------
Pydantic schemas for the Tea_entries collection.
"""

from pydantic import BaseModel, Field, model_validator
from typing import Optional
from datetime import date as Date
from app.models.base import TimestampMixin


# ── Create ───────────────────────────────────────────────────────────────────
class TeaEntryCreate(BaseModel):
    estateId: str
    workerId: str
    workerName: str
    date: Date = Field(..., example="2026-05-09")
    kg: float = Field(..., gt=0, example=24.5)
    ratePerKg: float = Field(..., gt=0, example=120.0)

    # totalAmount is computed automatically — the client does NOT send it
    totalAmount: Optional[float] = None

    @model_validator(mode="after")
    def compute_total(self):
        """Auto-calculate totalAmount = kg × ratePerKg."""
        self.totalAmount = round(self.kg * self.ratePerKg, 2)
        return self


# ── Update ───────────────────────────────────────────────────────────────────
class TeaEntryUpdate(BaseModel):
    kg: Optional[float] = Field(None, gt=0)
    ratePerKg: Optional[float] = Field(None, gt=0)


# ── Response ─────────────────────────────────────────────────────────────────
class TeaEntryResponse(TimestampMixin):
    teaEntryId: str
    estateId: str
    workerId: str
    workerName: str
    date: str
    kg: float
    ratePerKg: float
    totalAmount: float
    createdBy: str
