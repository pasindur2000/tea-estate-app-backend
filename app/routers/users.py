"""
routers/users.py
----------------
HTTP routes for User management.

Creating supervisors is DIRECTOR ONLY.
Viewing / editing profiles can be done by the authenticated user themselves
or by the director.
"""

from fastapi import APIRouter, Depends, HTTPException
from app.dependencies import get_current_user, director_only
from app.models.user import UserCreate, UserUpdate
from app.services import user_service
from app.utils.response import success_response

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", summary="Create a supervisor account [Director only]")
async def create_user(
    data: UserCreate,
    current_user: dict = Depends(director_only),
):
    user = await user_service.create_user(data)
    return success_response("User created successfully.", user)


@router.get("/estate/{estate_id}", summary="List users in an estate [Director only]")
async def list_users(estate_id: str, current_user: dict = Depends(director_only)):
    users = await user_service.list_users_by_estate(estate_id)
    return success_response("Users retrieved.", users)


@router.get("/me", summary="Get my own profile [Any authenticated user]")
async def get_my_profile(current_user: dict = Depends(get_current_user)):
    return success_response("Profile retrieved.", current_user)


@router.patch("/{uid}", summary="Update a user profile [Director only]")
async def update_user(
    uid: str,
    data: UserUpdate,
    current_user: dict = Depends(director_only),
):
    updated = await user_service.update_user(uid, data)
    if not updated:
        raise HTTPException(status_code=404, detail="User not found.")
    return success_response("User updated.", updated)


@router.delete("/{uid}", summary="Deactivate a user [Director only]")
async def deactivate_user(uid: str, current_user: dict = Depends(director_only)):
    done = await user_service.deactivate_user(uid)
    if not done:
        raise HTTPException(status_code=404, detail="User not found.")
    return success_response("User deactivated.")
