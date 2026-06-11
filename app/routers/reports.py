"""
routers/reports.py
------------------
Summary / expense reports. DIRECTOR ONLY.
"""

from fastapi import APIRouter, Depends, Query
from app.dependencies import director_only
from app.services import report_service
from app.utils.response import success_response

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get(
    "/tea-summary/{estate_id}",
    summary="Monthly tea harvest + earnings summary [Director only]",
)
async def monthly_tea_summary(
    estate_id: str,
    year: int = Query(..., example=2026),
    month: int = Query(..., ge=1, le=12, example=5),
    current_user: dict = Depends(director_only),
):
    report = await report_service.monthly_tea_summary(estate_id, year, month)
    return success_response("Monthly tea summary generated.", report)


@router.get(
    "/attendance-summary/{estate_id}",
    summary="Attendance summary for a date range [Director only]",
)
async def attendance_summary(
    estate_id: str,
    from_date: str = Query(..., example="2026-05-01"),
    to_date: str = Query(..., example="2026-05-31"),
    current_user: dict = Depends(director_only),
):
    report = await report_service.attendance_summary(estate_id, from_date, to_date)
    return success_response("Attendance summary generated.", report)
