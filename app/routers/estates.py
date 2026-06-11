"""
routers/estates.py
------------------
HTTP routes for the Estates resource.

All estate management is DIRECTOR ONLY.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from app.dependencies import get_current_user, director_only
from app.models.estate import EstateCreate, EstateUpdate
from app.services import estate_service
from app.utils.response import success_response, error_response

router = APIRouter(prefix="/estates", tags=["Estates"])


@router.post("/", summary="Create a new estate [Director only]")
async def create_estate(
    data: EstateCreate,
    current_user: dict = Depends(director_only),   # ← blocks non-directors
):
    estate = await estate_service.create_estate(data, current_user["uid"])
    return success_response("Estate created successfully.", estate)


@router.get("/", summary="List all estates [Director only]")
async def list_estates(current_user: dict = Depends(director_only)):
    estates = await estate_service.list_estates()
    return success_response("Estates retrieved.", estates)


@router.get("/{estate_id}", summary="Get a single estate [Director only]")
async def get_estate(estate_id: str, current_user: dict = Depends(director_only)):
    estate = await estate_service.get_estate(estate_id)
    if not estate:
        raise HTTPException(status_code=404, detail="Estate not found.")
    return success_response("Estate retrieved.", estate)


@router.patch("/{estate_id}", summary="Update an estate [Director only]")
async def update_estate(
    estate_id: str,
    data: EstateUpdate,
    current_user: dict = Depends(director_only),
):
    updated = await estate_service.update_estate(estate_id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="Estate not found.")
    return success_response("Estate updated.", updated)


@router.delete("/{estate_id}", summary="Deactivate an estate [Director only]")
async def delete_estate(estate_id: str, current_user: dict = Depends(director_only)):
    deleted = await estate_service.delete_estate(estate_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Estate not found.")
    return success_response("Estate deactivated.")
