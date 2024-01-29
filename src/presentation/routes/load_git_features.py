from flask import Blueprint

from src.app.controllers.extract_transform_load.load_features_from_repositories import (
    LoadFeaturesController,
)
from src.common.utils.json import jsonify
from src.infra.monitoring.logger import logger

blueprint_load_git_features = Blueprint("load_git_features", __name__)


@blueprint_load_git_features.route("/load_feat", methods=["GET"])
def load_git_features():
    try:
        controller = LoadFeaturesController(logger=logger)
        features = controller.execute(
            #  {"from_date": "2020-11-12", "to_date": "2020-11-13"}
        )
        return jsonify(features)

    except Exception as e:
        return (
            jsonify({"error": str(e)}),
            500,
        )
