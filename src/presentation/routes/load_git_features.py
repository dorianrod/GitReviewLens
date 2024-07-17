from typing import Optional

from fastapi import APIRouter, HTTPException

from src.app.controllers.extract_transform_load.load_features_from_repositories import (
    LoadFeaturesController,
)
from src.infra.monitoring.logger import logger

router = APIRouter()


@router.get("/load_features")
async def load_git_features(
    from_date: Optional[str] = None, to_date: Optional[str] = None
):
    try:
        controller = LoadFeaturesController(logger=logger)
        features = await controller.execute(
            {"from_date": from_date, "to_date": to_date}
        )
        return features
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": str(e)})
