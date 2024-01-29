from flask import Blueprint, jsonify

from src.app.controllers.getting_data.get_developers_from_database import (
    GetDevelopersController,
)
from src.infra.monitoring.logger import logger

blueprint_get_developers = Blueprint("get_developers", __name__)


@blueprint_get_developers.route("/developers", methods=["GET"])
def get_developers():
    try:
        controller = GetDevelopersController(logger=logger)
        developers = controller.execute()
        return jsonify([developer.to_dict() for developer in developers])

    except Exception as e:
        return (
            jsonify({"error": str(e)}),
            500,
        )
