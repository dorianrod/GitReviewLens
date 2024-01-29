from flask import Blueprint

from src.app.controllers.extract_transform_load.load_pull_requests_from_remote_origins import (
    LoadPullRequestsFromRemoteOriginController,
)
from src.common.utils.json import jsonify
from src.infra.monitoring.logger import logger

blueprint_load_pull_requests = Blueprint("load_pull_requests", __name__)


@blueprint_load_pull_requests.route("/load", methods=["GET"])
def load_pull_requests():
    try:
        controller = LoadPullRequestsFromRemoteOriginController(logger=logger)
        pull_requests_fro = controller.execute()

        return jsonify(pull_requests_fro)

    except Exception as e:
        return (
            jsonify({"error": str(e)}),
            500,
        )
