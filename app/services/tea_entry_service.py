"""
services/tea_entry_service.py
-----------------------------
All database operations for Tea Entries.
"""

from datetime import datetime, timezone
from app.config import get_firestore_client
from app.models.tea_entry import TeaEntryCreate, TeaEntryUpdate
import uuid


def _now():
    return datetime.now(timezone.utc)


async def create_tea_entry(data: TeaEntryCreate, created_by_uid: str) -> dict:
    db = get_firestore_client()
    entry_id = f"tea_{uuid.uuid4().hex[:8]}"

    doc = {
        "teaEntryId": entry_id,
        "estateId": data.estateId,
        "workerId": data.workerId,
        "workerName": data.workerName,
        "date": str(data.date),
        "kg": data.kg,
        "ratePerKg": data.ratePerKg,
        "totalAmount": data.totalAmount,     # computed by Pydantic validator
        "createdBy": created_by_uid,
        "createdAt": _now(),
        "updatedAt": _now(),
    }

    db.collection("Tea_entries").document(entry_id).set(doc)
    return doc


async def get_tea_entry(entry_id: str) -> dict | None:
    db = get_firestore_client()
    doc = db.collection("Tea_entries").document(entry_id).get()
    return doc.to_dict() if doc.exists else None


async def list_tea_entries(estate_id: str, date_filter: str | None = None) -> list[dict]:
    """
    Return tea entries for an estate.
    Optionally filter by a specific date string e.g. "2026-05-09".
    """
    db = get_firestore_client()
    query = db.collection("Tea_entries").where("estateId", "==", estate_id)
    if date_filter:
        query = query.where("date", "==", date_filter)
    results = [d.to_dict() for d in query.stream()]
    return sorted(results, key=lambda x: x.get("date", ""), reverse=True)


async def update_tea_entry(entry_id: str, data: TeaEntryUpdate) -> dict | None:
    db = get_firestore_client()
    ref = db.collection("Tea_entries").document(entry_id)
    existing = ref.get()
    if not existing.exists:
        return None

    current = existing.to_dict()
    kg = data.kg if data.kg is not None else current["kg"]
    rate = data.ratePerKg if data.ratePerKg is not None else current["ratePerKg"]

    updates = {
        "kg": kg,
        "ratePerKg": rate,
        "totalAmount": round(kg * rate, 2),
        "updatedAt": _now(),
    }
    ref.update(updates)
    return await get_tea_entry(entry_id)


async def delete_tea_entry(entry_id: str) -> bool:
    db = get_firestore_client()
    ref = db.collection("Tea_entries").document(entry_id)
    if not ref.get().exists:
        return False
    ref.delete()
    return True
