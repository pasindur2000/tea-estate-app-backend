"""
routers/tea_entries.py
----------------------
Both roles can create and view tea entries.
Only directors can delete entries.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from app.dependencies import get_current_user, director_only
from app.models.tea_entry import TeaEntryCreate, TeaEntryUpdate
from app.services import tea_entry_service
from app.utils.response import success_response

router = APIRouter(prefix="/tea-entries", tags=["Tea Entries"])


@router.post("/", summary="Add a tea entry [Director or Supervisor]")
async def create_entry(
    data: TeaEntryCreate,
    current_user: dict = Depends(get_current_user),
):
    entry = await tea_entry_service.create_tea_entry(data, current_user["uid"])
    return success_response("Tea entry recorded.", entry)


@router.get("/estate/{estate_id}", summary="List entries for an estate [Any user]")
async def list_entries(
    estate_id: str,
    date: Optional[str] = Query(None, description="Filter by date e.g. 2026-05-09"),
    current_user: dict = Depends(get_current_user),
):
    entries = await tea_entry_service.list_tea_entries(estate_id, date)
    return success_response("Tea entries retrieved.", entries)


@router.get("/{entry_id}", summary="Get a single tea entry [Any user]")
async def get_entry(entry_id: str, current_user: dict = Depends(get_current_user)):
    entry = await tea_entry_service.get_tea_entry(entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Tea entry not found.")
    return success_response("Tea entry retrieved.", entry)


@router.patch("/{entry_id}", summary="Update a tea entry [Director or Supervisor]")
async def update_entry(
    entry_id: str,
    data: TeaEntryUpdate,
    current_user: dict = Depends(get_current_user),
):
    updated = await tea_entry_service.update_tea_entry(entry_id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="Tea entry not found.")
    return success_response("Tea entry updated.", updated)


@router.delete("/{entry_id}", summary="Delete a tea entry [Director only]")
async def delete_entry(entry_id: str, current_user: dict = Depends(director_only)):
    done = await tea_entry_service.delete_tea_entry(entry_id)
    if not done:
        raise HTTPException(status_code=404, detail="Tea entry not found.")
    return success_response("Tea entry deleted.")
