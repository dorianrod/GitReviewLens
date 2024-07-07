from datetime import datetime

from flask import Blueprint

from src.common.utils.date import parse_date
from src.common.utils.json import jsonify
from src.domain.repositories.pull_requests import PullRequestsRepository
from src.infra.monitoring.logger import LoggerDefault
from src.infra.repositories.azure.pull_requests import PullRequestsAzureRepository
from src.settings import settings

blueprint_test = Blueprint("test", __name__)


@blueprint_test.route("/test", methods=["GET"])
async def test():
    try:
        branches = settings.get_branches()
        branch = branches[0]

        repository = branch.repository

        options = {
            "logger": LoggerDefault(),
            "git_repository": repository,
        }

        remote_repository: PullRequestsRepository = PullRequestsAzureRepository(
            **options
        )

        try:
            result = await remote_repository.find_all(
                {
                    "start_date": parse_date(datetime.now()),
                    "end_date": parse_date(datetime.now()),
                }  # type: ignore
            )
            return jsonify(result)
        except Exception as e:
            print(e)

    except Exception as e:
        return (
            jsonify({"error": str(e)}),
            500,
        )
