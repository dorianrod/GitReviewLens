from src.app.controllers.getting_data.get_pull_requests_from_database import (
    GetPullRequestsController,
)
from src.domain.entities.pull_request import PullRequest
from src.infra.repositories.postgresql.pull_requests import (
    PullRequestsDatabaseRepository,
)


async def test_get_pull_requests(mock_logger, fixture_pull_request_dict):
    controller = GetPullRequestsController(
        logger=mock_logger, git_repository="orga/project/Backend"
    )
    db_repo = PullRequestsDatabaseRepository(
        logger=mock_logger, git_repository="orga/project/Backend"
    )

    pull_request = PullRequest.from_dict(
        {**fixture_pull_request_dict, "git_repository": "orga/project/Backend"}
    )
    await db_repo.upsert(
        PullRequest.from_dict(
            {**fixture_pull_request_dict, "git_repository": "orga/project/Backend"}
        )
    )

    assert await controller.execute() == [pull_request]
