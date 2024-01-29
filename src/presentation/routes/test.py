from flask import Blueprint

from src.app.controllers.database_dump_and_init.init_database import (
    InitDatabaseController,
)
from src.common.utils.json import jsonify
from src.infra.monitoring.logger import LoggerDefault

blueprint_test = Blueprint("test", __name__)


@blueprint_test.route("/test", methods=["GET"])
def test():
    try:
        InitDatabaseController(logger=LoggerDefault()).execute()
        return jsonify([])

    except Exception as e:
        return (
            jsonify({"error": str(e)}),
            500,
        )
