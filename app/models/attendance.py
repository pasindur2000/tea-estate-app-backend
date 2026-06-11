"""
models/attendance.py
--------------------
Pydantic schemas for the Attendance collection.
"""

from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import date as Date
from app.models.base import TimestampMixin


# ── Create ───────────────────────────────────────────────────────────────────
class AttendanceCreate(BaseModel):
    estateId: str
    workerId: str
    workerName: str
    date: Date = Field(..., example="2026-05-09")
    status: Literal["present", "absent", "half_day"] = "present"


# ── Update ───────────────────────────────────────────────────────────────────
class AttendanceUpdate(BaseModel):
    status: Optional[Literal["present", "absent", "half_day"]] = None


# ── Response ─────────────────────────────────────────────────────────────────
class AttendanceResponse(TimestampMixin):
    attendanceId: str
    estateId: str
    workerId: str
    workerName: str
    date: str
    status: str
    createdBy: str
