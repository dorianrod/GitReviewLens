from flask import Flask, g
from werkzeug.exceptions import HTTPException

from src.common.monitoring.logger import LoggerInterface
from src.infra.database.postgresql.database import init_db
from src.presentation.routes import routes


def create_app(logger: LoggerInterface):
    app = Flask(__name__)
    app.config["logger"] = logger
    app.config["TIMEOUT"] = 60 * 10  # Loading can be slow

    init_db(app)

    for route in routes:
        app.register_blueprint(route, url_prefix="/")

    @app.errorhandler(HTTPException)
    def handle_http_error(error: HTTPException):
        """Handle HTTP Error Response"""
        logger.exception(str(error.__class__.__name__))
        logger.exception(str(error.description))
        response = {
            "error": error.__class__.__name__,
            "message": error.description,
        }
        return response, error.code

    @app.errorhandler(ValueError)
    def handle_value_error(error: ValueError):
        """Handle Value Error Response"""
        return format_error_response(error, 400, logger)

    @app.errorhandler(Exception)
    def handle_general_exception(error):
        """Handle Other Errors Response"""
        return format_error_response(error, 500, logger)

    @app.teardown_request
    def teardown_request(_unused=False):
        """After Request"""
        dbc = getattr(g, "db", None)
        if dbc is not None:
            dbc.close()

    return app


def format_error_response(error: Exception, error_code: int, logger: LoggerInterface):
    logger.exception(f"500 - Internal Server Error: {str(error)}")

    response = {
        "status_code": error_code,
        "error": error.__class__.__name__,
        "message": str(error),
    }
    return response, error_code
