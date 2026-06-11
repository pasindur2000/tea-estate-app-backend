"""
services/user_service.py
------------------------
Business logic for managing users (directors & supervisors).
Creating a user here also creates a Firebase Auth account.
"""

from datetime import datetime, timezone
from app.config import get_firestore_client, firebase_auth
from app.models.user import UserCreate, UserUpdate
from fastapi import HTTPException, status


def _now():
    return datetime.now(timezone.utc)


async def create_user(data: UserCreate) -> dict:
    """
    1. Create a Firebase Auth account (email + password).
    2. Save the user profile in Firestore Users collection.
    """
    db = get_firestore_client()

    # ── Step 1: Create Firebase Auth account ─────────────────────────────────
    try:
        auth_user = firebase_auth.create_user(
            email=data.email,
            password=data.password,
            display_name=data.name,
        )
    except firebase_auth.EmailAlreadyExistsError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists.",
        )

    uid = auth_user.uid

    # ── Step 2: Save profile to Firestore ────────────────────────────────────
    doc = {
        "uid": uid,
        "name": data.name,
        "email": data.email,
        "role": data.role,
        "estateId": data.estateId,
        "status": "active",
        "createdAt": _now(),
        "updatedAt": _now(),
    }

    db.collection("Users").document(uid).set(doc)
    return doc


async def get_user(uid: str) -> dict | None:
    db = get_firestore_client()
    doc = db.collection("Users").document(uid).get()
    return doc.to_dict() if doc.exists else None


async def list_users_by_estate(estate_id: str, role: str | None = None) -> list[dict]:
    """List users for an estate. Optionally filter by role."""
    db = get_firestore_client()
    query = db.collection("Users").where("estateId", "==", estate_id)
    if role:
        query = query.where("role", "==", role)
    docs = query.stream()
    return [d.to_dict() for d in docs]


async def update_user(uid: str, data: UserUpdate) -> dict | None:
    db = get_firestore_client()
    ref = db.collection("Users").document(uid)
    updates = {k: v for k, v in data.model_dump().items() if v is not None}
    if updates:
        updates["updatedAt"] = _now()
        ref.update(updates)
    return await get_user(uid)


async def deactivate_user(uid: str) -> bool:
    db = get_firestore_client()
    ref = db.collection("Users").document(uid)
    if not ref.get().exists:
        return False
    # Disable in Firebase Auth too
    firebase_auth.update_user(uid, disabled=True)
    ref.update({"status": "inactive", "updatedAt": _now()})
    return True
