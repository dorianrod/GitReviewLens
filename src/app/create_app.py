from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from src.common.monitoring.logger import LoggerInterface
from src.infra.database.postgresql.database import init_db
from src.presentation.routes import routes


async def create_app(logger):
    app = FastAPI()
    app.state.logger = logger
    app.state.TIMEOUT = 60

    await init_db()

    for route in routes:
        app.include_router(route)

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """Handle HTTP Error Response"""
        logger.exception(f"{exc.__class__.__name__}: {exc.detail}")
        response = {
            "error": exc.__class__.__name__,
            "message": exc.detail,
        }
        return JSONResponse(status_code=exc.status_code, content=response)

    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError):
        """Handle Value Error Response"""
        return await format_error_response(exc, 400, logger)

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle Other Errors Response"""
        return await format_error_response(exc, 500, logger)

    @app.middleware("http")
    async def db_session_middleware(request: Request, call_next):
        """Middleware to handle DB session teardown"""
        response = await call_next(request)
        # Assuming you have a global DB connection in request state
        db_conn = request.state.db if hasattr(request.state, "db") else None
        if db_conn:
            db_conn.close()
        return response

    return app


async def format_error_response(
    error: Exception, error_code: int, logger: LoggerInterface
):
    logger.exception(f"{error_code} - {error.__class__.__name__}: {str(error)}")

    response = {
        "status_code": error_code,
        "error": error.__class__.__name__,
        "message": str(error),
    }
    return JSONResponse(status_code=error_code, content=response)
