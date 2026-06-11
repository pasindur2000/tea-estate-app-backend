"""
services/estate_service.py
--------------------------
All database operations for Estates live here.

The SERVICE LAYER keeps business logic OUT of the routers.
Routers only handle HTTP; services handle data.
"""

from datetime import datetime, timezone
from google.cloud.firestore_v1 import SERVER_TIMESTAMP
from app.config import get_firestore_client
from app.models.estate import EstateCreate, EstateUpdate
import uuid


def _now() -> datetime:
    return datetime.now(timezone.utc)


async def create_estate(data: EstateCreate, created_by_uid: str) -> dict:
    """Create a new estate document in Firestore."""
    db = get_firestore_client()
    estate_id = f"estate_{uuid.uuid4().hex[:8]}"

    doc = {
        "estateId": estate_id,
        "name": data.name,
        "location": data.location,
        "status": data.status,
        "createdBy": created_by_uid,
        "createdAt": _now(),
        "updatedAt": _now(),
    }

    db.collection("Estates").document(estate_id).set(doc)
    return doc


async def get_estate(estate_id: str) -> dict | None:
    """Get a single estate by ID. Returns None if not found."""
    db = get_firestore_client()
    doc = db.collection("Estates").document(estate_id).get()
    return doc.to_dict() if doc.exists else None


async def list_estates() -> list[dict]:
    """Return all estates."""
    db = get_firestore_client()
    docs = db.collection("Estates").order_by("createdAt").stream()
    return [d.to_dict() for d in docs]


async def update_estate(estate_id: str, data: EstateUpdate) -> dict | None:
    """Update only the fields that were provided (partial update)."""
    db = get_firestore_client()
    ref = db.collection("Estates").document(estate_id)

    # Build update dict — skip fields the caller left as None
    updates = {k: v for k, v in data.model_dump().items() if v is not None}
    if not updates:
        return await get_estate(estate_id)   # nothing to change

    updates["updatedAt"] = _now()
    ref.update(updates)
    return (await get_estate(estate_id))


async def delete_estate(estate_id: str) -> bool:
    """Soft-delete by setting status = inactive."""
    db = get_firestore_client()
    ref = db.collection("Estates").document(estate_id)
    if not ref.get().exists:
        return False
    ref.update({"status": "inactive", "updatedAt": _now()})
    return True
