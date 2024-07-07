from unittest.mock import patch

import pytest

from src.app.controllers.extract_transform_load.load_pull_requests_from_remote_origins import (
    LoadPullRequestsFromRemoteOriginController,
)
from src.common.utils.date import parse_date
from src.domain.entities.pull_request import PullRequest
from src.domain.use_cases.transfer_pull_requests_from_repositories import (
    TransferPullRequestsToAnotherRepositoryUseCase,
)
from src.infra.repositories.postgresql.pull_requests import (
    PullRequestsDatabaseRepository,
)


@pytest.fixture(scope="function", autouse=True)
def mock_settings(mocker, mock_git_settings):
    mocker.patch(
        "src.app.controllers.extract_transform_load.load_pull_requests_from_remote_origins.settings",
        mock_git_settings,
    )


async def test_call_use_case_for_each_repo(mock_logger, mock_git_settings):
    with patch.object(
        LoadPullRequestsFromRemoteOriginController,
        'load_from_repository',
        return_value=[],
    ) as mock:
        controller = LoadPullRequestsFromRemoteOriginController(logger=mock_logger)
        await controller.execute()

        repositories = mock_git_settings.get_branches()

        assert mock.call_count == len(repositories)
        assert mock.call_args_list[0].kwargs == {
            "git_repository": repositories[0].repository,
            "options": None,
        }
        assert mock.call_args_list[1].kwargs == {
            "git_repository": repositories[1].repository,
            "options": None,
        }


async def test_only_loads_new_pull_requests(
    mock_logger,
    mock_git_settings,
    fixture_pull_request_dict,
):
    with patch.object(
        TransferPullRequestsToAnotherRepositoryUseCase,
        'execute',
        return_value=[],
    ) as mock_usecase:
        git_repository = mock_git_settings.get_branches()[0].repository
        db_repo = PullRequestsDatabaseRepository(
            logger=mock_logger, git_repository=git_repository
        )
        await db_repo.upsert(
            PullRequest.from_dict(
                {**fixture_pull_request_dict, "git_repository": git_repository}
            )
        )
        await db_repo.upsert(
            PullRequest.from_dict(
                {
                    **fixture_pull_request_dict,
                    "source_id": 11,
                    "completion_date": "2021-10-25T11:10:13",
                    "git_repository": git_repository,
                }
            )
        )

        controller = LoadPullRequestsFromRemoteOriginController(logger=mock_logger)
        await controller.execute()

        assert mock_usecase.call_count == len(mock_git_settings.get_branches())
        mock_usecase.assert_any_call(
            {"start_date": parse_date(fixture_pull_request_dict["completion_date"])}
        )
