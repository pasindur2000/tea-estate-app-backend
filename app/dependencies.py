"""
dependencies.py
---------------
FastAPI "dependencies" are functions that run BEFORE a route handler.
We use them here to:
  1. Extract the Bearer token from the Authorization header.
  2. Verify it with Firebase Auth (rejects expired / fake tokens).
  3. Look up the user in Firestore so we know their role and estateId.
  4. Make the current user available to every route handler.

How to use in a route:
    @router.get("/something")
    async def my_route(current_user: dict = Depends(get_current_user)):
        print(current_user["role"])  # "director" or "supervisor"
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.config import firebase_auth, get_firestore_client

# This tells FastAPI to look for "Authorization: Bearer <token>" in the request header
bearer_scheme = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> dict:
    """
    Dependency that:
    1. Verifies the Firebase ID token from the request header.
    2. Loads the matching user document from Firestore.
    3. Returns the user dict (uid, name, email, role, estateId, status).

    Raises HTTP 401 if the token is invalid or expired.
    Raises HTTP 403 if the user account is inactive.
    """
    token = credentials.credentials  # the raw JWT string

    # ── Step 1: Verify token with Firebase ───────────────────────────────────
    try:
        decoded_token = firebase_auth.verify_id_token(token)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token.",
        )

    uid = decoded_token["uid"]

    # ── Step 2: Load user from Firestore ─────────────────────────────────────
    db = get_firestore_client()
    user_doc = db.collection("Users").document(uid).get()

    if not user_doc.exists:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User record not found.",
        )

    user_data = user_doc.to_dict()

    # ── Step 3: Make sure the account is still active ────────────────────────
    if user_data.get("status") != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account has been deactivated.",
        )

    return user_data  # passed into route handlers as `current_user`


# ── Role-based shortcut dependencies ─────────────────────────────────────────
# Use these in routes that need a specific role.

async def director_only(current_user: dict = Depends(get_current_user)) -> dict:
    """Allows only users with role == 'director'."""
    if current_user.get("role") != "director":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only directors can perform this action.",
        )
    return current_user


async def any_authenticated_user(current_user: dict = Depends(get_current_user)) -> dict:
    """Allows any authenticated user (director or supervisor)."""
    return current_user
