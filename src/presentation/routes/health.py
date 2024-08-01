from fastapi import APIRouter
from fastapi.responses import JSONResponse

from src.common.settings import settings

router = APIRouter()


@router.get("/", response_class=JSONResponse)
@router.get("/health", response_class=JSONResponse)
async def get_application_state():
    return {"status": "OK", "version": settings.version}
