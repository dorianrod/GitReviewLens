from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from src.app.controllers.getting_data.get_features_from_database import (
    GetFeaturesController,
)
from src.domain.entities.repository import Repository
from src.infra.monitoring.logger import logger

router = APIRouter()


@router.get("/features", response_class=JSONResponse)
async def get_features(repository: str):
    try:
        repo = Repository.parse(repository)
        controller = GetFeaturesController(logger=logger, git_repository=repo)
        features = await controller.execute()
        return [feature.to_dict() for feature in features]
    except Exception as e:
        logger.error(f"Error fetching features: {str(e)}")
        raise HTTPException(status_code=500, detail={"error": str(e)})
