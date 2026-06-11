"""
routers/attendance.py
---------------------
Both roles can record and view attendance.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from app.dependencies import get_current_user
from app.models.attendance import AttendanceCreate, AttendanceUpdate
from app.services import attendance_service
from app.utils.response import success_response

router = APIRouter(prefix="/attendance", tags=["Attendance"])


@router.post("/", summary="Mark attendance [Director or Supervisor]")
async def create_attendance(
    data: AttendanceCreate,
    current_user: dict = Depends(get_current_user),
):
    record = await attendance_service.create_attendance(data, current_user["uid"])
    return success_response("Attendance recorded.", record)


@router.get("/estate/{estate_id}", summary="List attendance [Any user]")
async def list_attendance(
    estate_id: str,
    date: Optional[str] = Query(None, description="Filter by date e.g. 2026-05-09"),
    current_user: dict = Depends(get_current_user),
):
    records = await attendance_service.list_attendance(estate_id, date)
    return success_response("Attendance records retrieved.", records)


@router.patch("/{att_id}", summary="Update attendance status [Director or Supervisor]")
async def update_attendance(
    att_id: str,
    data: AttendanceUpdate,
    current_user: dict = Depends(get_current_user),
):
    updated = await attendance_service.update_attendance(att_id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="Attendance record not found.")
    return success_response("Attendance updated.", updated)
