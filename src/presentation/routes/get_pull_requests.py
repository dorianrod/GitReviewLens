from typing import List

from fastapi import APIRouter, HTTPException

from src.app.controllers.getting_data.get_pull_requests_from_database import (
    GetPullRequestsController,
)
from src.domain.entities.repository import Repository
from src.infra.monitoring.logger import logger

router = APIRouter()


@router.get("/pull_requests", response_model=List[dict])
async def get_pull_requests(repository: str):
    try:
        controller = GetPullRequestsController(
            logger=logger,
            git_repository=Repository.parse(repository),
        )
        pull_requests = await controller.execute()
        return [pull_request.to_dict() for pull_request in pull_requests]
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": str(e)})
