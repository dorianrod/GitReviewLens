from fastapi import APIRouter, HTTPException

from src.app.controllers.extract_transform_load.load_pull_requests_from_remote_origins import (
    LoadPullRequestsFromRemoteOriginController,
)
from src.infra.monitoring.logger import logger

router = APIRouter()


@router.get("/load_pull_requests")
async def load_pull_requests():
    try:
        controller = LoadPullRequestsFromRemoteOriginController(logger=logger)
        pull_requests = await controller.execute()
        return pull_requests
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": str(e)})
