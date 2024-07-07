from unittest.mock import AsyncMock, patch

import pytest

from src.app.controllers.extract_transform_load.load_pull_requests_from_remote_origins import (
    LoadPullRequestsFromRemoteOriginController,
)
from src.common.utils.date import parse_date
from src.common.utils.worker import concurrency_aio
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
    call_args_list = []

    @concurrency_aio(max_concurrency=5)
    async def load_from_repository(self, git_repository, options):
        call_args_list.append((git_repository, options))

    with patch.object(
        LoadPullRequestsFromRemoteOriginController,
        'load_from_repository',
        new=load_from_repository,
    ):
        controller = LoadPullRequestsFromRemoteOriginController(logger=mock_logger)
        await controller.execute()

        repositories = mock_git_settings.get_branches()

        assert len(call_args_list) == len(repositories)

        for index, kwargs in enumerate(call_args_list):
            assert kwargs == (repositories[index].repository, None)


async def test_only_loads_new_pull_requests(
    mock_logger,
    mock_git_settings,
    fixture_pull_request_dict,
):
    with patch.object(
        TransferPullRequestsToAnotherRepositoryUseCase,
        'execute',
        return_value=AsyncMock(return_value=[]),
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
