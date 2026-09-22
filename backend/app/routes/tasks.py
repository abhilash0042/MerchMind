"""Task status routes — /tasks/*"""
from fastapi import APIRouter, Depends, HTTPException

from app.core.security import require_api_key
from workers.celery_app import celery_app

router = APIRouter(dependencies=[Depends(require_api_key)])


@router.get("/{task_id}", summary="Get Celery task status")
async def get_task_status(task_id: str):
    """
    Returns Celery task status and (if finished) the result.
    Useful for polling long-running embedding jobs.
    """
    async_result = celery_app.AsyncResult(task_id)
    status = async_result.status

    response = {"task_id": task_id, "status": status}

    if async_result.failed():
        # Don't expose full traceback, just a message.
        response["error"] = str(async_result.result)
    elif async_result.successful():
        response["result"] = async_result.result

    return response

