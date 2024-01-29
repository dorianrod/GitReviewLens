from flask import Blueprint, jsonify, request

from src.app.controllers.getting_data.get_features_from_database import (
    GetFeaturesController,
)
from src.domain.entities.repository import Repository
from src.infra.monitoring.logger import logger

blueprint_get_features = Blueprint("get_features", __name__)


@blueprint_get_features.route("/features", methods=["GET"])
def get_features():
    try:
        controller = GetFeaturesController(
            logger=logger, git_repository=Repository.parse(request.args["repository"])
        )
        features = controller.execute()
        return jsonify([feature.to_dict() for feature in features])

    except Exception as e:
        return (
            jsonify({"error": str(e)}),
            500,
        )
