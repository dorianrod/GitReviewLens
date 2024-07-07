import pytest
import requests_mock

from src.domain.entities.pull_request import PullRequest
from src.infra.repositories.github.approvers import ApproversGithubRepository


@pytest.fixture
def repository(mock_logger):
    return ApproversGithubRepository(
        logger=mock_logger,
        git_repository={
            "name": "myrepo",
            "organisation": "orga",
        },
    )


@pytest.fixture
def pull_request(fixture_pull_request_dict):
    return PullRequest.from_dict(
        {**fixture_pull_request_dict, "git_repository": "orga/myrepo"}
    )


async def test_does_approvers(
    mocker, mock_approver_in_github, repository, pull_request
):
    with requests_mock.Mocker() as mocker:
        mocker.get(
            f"https://api.github.com/repos/orga/myrepo/pulls/{pull_request.source_id}/reviews?per_page=100&page=1",
            json=[mock_approver_in_github],
        )

        approvers = await repository.find_all({"pull_request": pull_request})

        assert len(approvers) == 1
        assert approvers[0].to_dict() == {
            'email': 'approveruser@github.com',
            'full_name': 'approveruser',
            'id': 'approveruser@github.com',
        }


async def test_does_use_pagination(
    mocker,
    mock_approver_in_github,
    mock_approver_2_in_github,
    repository,
    pull_request,
):
    with requests_mock.Mocker() as mocker:
        mocker.get(
            f"https://api.github.com/repos/orga/myrepo/pulls/{pull_request.source_id}/reviews?per_page=1&page=1",
            json=[mock_approver_in_github],
        )
        mocker.get(
            f"https://api.github.com/repos/orga/myrepo/pulls/{pull_request.source_id}/reviews?per_page=1&page=2",
            json=[mock_approver_2_in_github],
        )
        mocker.get(
            f"https://api.github.com/repos/orga/myrepo/pulls/{pull_request.source_id}/reviews?per_page=1&page=3",
            json=[],
        )

        repository.max_results = 1
        pull_requests = await repository.find_all(
            filters={"pull_request": pull_request}
        )

        assert len(pull_requests) == 2


async def test_filters_out_comments(
    mocker,
    mock_commenter_in_github,
    repository,
    pull_request,
):
    with requests_mock.Mocker() as mocker:
        mocker.get(
            f"https://api.github.com/repos/orga/myrepo/pulls/{pull_request.source_id}/reviews?per_page=100&page=1",
            json=[
                mock_commenter_in_github,
            ],
        )

        pull_requests = await repository.find_all(
            filters={"pull_request": pull_request}
        )

        assert len(pull_requests) == 0
