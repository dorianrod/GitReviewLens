from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from src.app.controllers.getting_data.get_developers_from_database import (
    GetDevelopersController,
)
from src.infra.monitoring.logger import logger

router = APIRouter()


@router.get("/developers", response_class=JSONResponse)
async def get_developers():
    try:
        controller = GetDevelopersController(logger=logger)
        developers = await controller.execute()
        return [developer.to_dict() for developer in developers]
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": str(e)})
