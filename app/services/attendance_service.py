"""
services/attendance_service.py
-------------------------------
Database operations for Attendance records.
"""

from datetime import datetime, timezone
from app.config import get_firestore_client
from app.models.attendance import AttendanceCreate, AttendanceUpdate
import uuid


def _now():
    return datetime.now(timezone.utc)


async def create_attendance(data: AttendanceCreate, created_by_uid: str) -> dict:
    db = get_firestore_client()
    att_id = f"attendance_{uuid.uuid4().hex[:8]}"

    doc = {
        "attendanceId": att_id,
        "estateId": data.estateId,
        "workerId": data.workerId,
        "workerName": data.workerName,
        "date": str(data.date),
        "status": data.status,
        "createdBy": created_by_uid,
        "createdAt": _now(),
        "updatedAt": _now(),
    }

    db.collection("Attendance").document(att_id).set(doc)
    return doc


async def get_attendance(att_id: str) -> dict | None:
    db = get_firestore_client()
    doc = db.collection("Attendance").document(att_id).get()
    return doc.to_dict() if doc.exists else None


async def list_attendance(estate_id: str, date_filter: str | None = None) -> list[dict]:
    db = get_firestore_client()
    query = db.collection("Attendance").where("estateId", "==", estate_id)
    if date_filter:
        query = query.where("date", "==", date_filter)
    docs = query.order_by("date", direction="DESCENDING").stream()
    return [d.to_dict() for d in docs]


async def update_attendance(att_id: str, data: AttendanceUpdate) -> dict | None:
    db = get_firestore_client()
    ref = db.collection("Attendance").document(att_id)
    if not ref.get().exists:
        return None
    updates = {k: v for k, v in data.model_dump().items() if v is not None}
    if updates:
        updates["updatedAt"] = _now()
        ref.update(updates)
    return await get_attendance(att_id)
