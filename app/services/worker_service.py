"""
services/worker_service.py
--------------------------
All database operations for Workers.
"""

from datetime import datetime, timezone
from app.config import get_firestore_client
from app.models.worker import WorkerCreate, WorkerUpdate
import uuid


def _now():
    return datetime.now(timezone.utc)


async def create_worker(data: WorkerCreate, created_by_uid: str) -> dict:
    db = get_firestore_client()
    worker_id = f"worker_{uuid.uuid4().hex[:8]}"

    doc = {
        "workerId": worker_id,
        "estateId": data.estateId,
        "name": data.name,
        "nic": data.nic,
        "phone": data.phone,
        "status": data.status,
        "joinedDate": str(data.joinedDate),
        "createdBy": created_by_uid,
        "createdAt": _now(),
        "updatedAt": _now(),
    }

    db.collection("Workers").document(worker_id).set(doc)
    return doc


async def get_worker(worker_id: str) -> dict | None:
    db = get_firestore_client()
    doc = db.collection("Workers").document(worker_id).get()
    return doc.to_dict() if doc.exists else None


async def list_workers_by_estate(estate_id: str) -> list[dict]:
    """Return all workers that belong to a specific estate."""
    db = get_firestore_client()
    docs = (
        db.collection("Workers")
        .where("estateId", "==", estate_id)
        .where("status", "==", "active")
        .stream()
    )
    return [d.to_dict() for d in docs]


async def update_worker(worker_id: str, data: WorkerUpdate) -> dict | None:
    db = get_firestore_client()
    ref = db.collection("Workers").document(worker_id)
    updates = {k: v for k, v in data.model_dump().items() if v is not None}
    if updates:
        updates["updatedAt"] = _now()
        ref.update(updates)
    return await get_worker(worker_id)


async def delete_worker(worker_id: str) -> bool:
    db = get_firestore_client()
    ref = db.collection("Workers").document(worker_id)
    if not ref.get().exists:
        return False
    ref.update({"status": "inactive", "updatedAt": _now()})
    return True
