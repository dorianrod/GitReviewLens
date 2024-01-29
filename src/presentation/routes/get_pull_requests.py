from flask import Blueprint, jsonify, request

from src.app.controllers.getting_data.get_pull_requests_from_database import (
    GetPullRequestsController,
)
from src.domain.entities.repository import Repository
from src.infra.monitoring.logger import logger

blueprint_get_pull_requests = Blueprint("get_pull_requests", __name__)


@blueprint_get_pull_requests.route("/pull_requests", methods=["GET"])
def get_pull_requests():
    try:
        controller = GetPullRequestsController(
            logger=logger, git_repository=Repository.parse(request.args["repository"])
        )
        pull_requests = controller.execute()
        return jsonify([pull_request.to_dict() for pull_request in pull_requests])

    except Exception as e:
        return (
            jsonify({"error": str(e)}),
            500,
        )
