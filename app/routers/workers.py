"""
routers/workers.py
------------------
Both directors AND supervisors can add / view workers.
Only directors can deactivate workers.
"""

from fastapi import APIRouter, Depends, HTTPException
from app.dependencies import get_current_user, director_only
from app.models.worker import WorkerCreate, WorkerUpdate
from app.services import worker_service
from app.utils.response import success_response

router = APIRouter(prefix="/workers", tags=["Workers"])


@router.post("/", summary="Add a worker [Director or Supervisor]")
async def create_worker(
    data: WorkerCreate,
    current_user: dict = Depends(get_current_user),   # any logged-in user
):
    worker = await worker_service.create_worker(data, current_user["uid"])
    return success_response("Worker added successfully.", worker)


@router.get("/estate/{estate_id}", summary="List workers in an estate [Any user]")
async def list_workers(estate_id: str, current_user: dict = Depends(get_current_user)):
    workers = await worker_service.list_workers_by_estate(estate_id)
    return success_response("Workers retrieved.", workers)


@router.get("/{worker_id}", summary="Get a worker [Any user]")
async def get_worker(worker_id: str, current_user: dict = Depends(get_current_user)):
    worker = await worker_service.get_worker(worker_id)
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found.")
    return success_response("Worker retrieved.", worker)


@router.patch("/{worker_id}", summary="Update a worker [Director or Supervisor]")
async def update_worker(
    worker_id: str,
    data: WorkerUpdate,
    current_user: dict = Depends(get_current_user),
):
    updated = await worker_service.update_worker(worker_id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="Worker not found.")
    return success_response("Worker updated.", updated)


@router.delete("/{worker_id}", summary="Deactivate a worker [Director only]")
async def deactivate_worker(worker_id: str, current_user: dict = Depends(director_only)):
    done = await worker_service.delete_worker(worker_id)
    if not done:
        raise HTTPException(status_code=404, detail="Worker not found.")
    return success_response("Worker deactivated.")
