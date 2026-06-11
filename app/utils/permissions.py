"""
utils/permissions.py
---------------------
Defines role constants and a simple permission system.

How it works:
  Every route that needs a specific role calls `require_role(["director"])`.
  If the logged-in user's role is NOT in that list, the request is rejected
  with a 403 Forbidden error before the route handler even runs.
"""

from fastapi import HTTPException, status


# ── Role Constants ────────────────────────────────────────────────────────────
DIRECTOR = "director"
SUPERVISOR = "supervisor"

# Shorthand groups used in routes
ALL_ROLES = [DIRECTOR, SUPERVISOR]
DIRECTOR_ONLY = [DIRECTOR]


# ── Permission Checker ────────────────────────────────────────────────────────
def require_role(allowed_roles: list[str]):
    """
    Returns a FastAPI dependency that raises HTTP 403 if the current
    user's role is not in `allowed_roles`.

    Usage in a router:
        @router.post("/estates", dependencies=[Depends(require_role(DIRECTOR_ONLY))])
    """
    def _check(current_user: dict):
        if current_user.get("role") not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role(s): {allowed_roles}",
            )
    return _check
