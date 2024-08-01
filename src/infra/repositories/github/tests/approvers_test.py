import pytest

from src.domain.entities.pull_request import PullRequest
from src.infra.repositories.github.approvers import ApproversGithubRepository


@pytest.fixture
def repository(mock_logger):
    return ApproversGithubRepository(
        logger=mock_logger,
        pagination={
            "max_concurrency": 1,
            "items_per_page": 100,
        },
        git_repository={
            "name": "myrepo",
            "organisation": "orga",
        },
    )


@pytest.fixture
def repository_pagination(mock_logger):
    return ApproversGithubRepository(
        logger=mock_logger,
        pagination={
            "max_concurrency": 1,
            "items_per_page": 1,
        },
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
    mock_approver_in_github, mock_api_approvers, repository, pull_request
):
    mock_api_approvers(pull_request.source_id, [mock_approver_in_github])

    approvers_for_pull_requests = await repository.find_all(
        {"pull_requests": [pull_request]}
    )

    assert len(approvers_for_pull_requests) == 1

    approvers, _ = approvers_for_pull_requests[0]
    assert len(approvers) == 1
    assert approvers[0].to_dict() == {
        'email': 'approveruser@github.com',
        'full_name': 'approveruser',
        'id': 'approveruser@github.com',
    }


async def test_does_use_pagination(
    mock_approver_in_github,
    mock_approver_2_in_github,
    repository_pagination,
    pull_request,
    mock_api_approvers,
):
    mock_api_approvers(
        pull_request.source_id, [mock_approver_in_github], per_page=1, page=1
    )
    mock_api_approvers(
        pull_request.source_id, [mock_approver_2_in_github], per_page=1, page=2
    )
    mock_api_approvers(pull_request.source_id, [], per_page=1, page=3)

    approvers_for_pull_requests = await repository_pagination.find_all(
        {"pull_requests": [pull_request]}
    )

    assert len(approvers_for_pull_requests) == 1

    approvers, pull_request_for_approvers = approvers_for_pull_requests[0]
    assert len(approvers) == 2
    assert pull_request_for_approvers == pull_request


async def test_filters_out_comments(
    mock_commenter_in_github, repository, pull_request, mock_api_approvers
):
    mock_api_approvers(pull_request.source_id, [mock_commenter_in_github])

    approvers_for_pull_requests = await repository.find_all(
        {"pull_requests": [pull_request]}
    )

    assert len(approvers_for_pull_requests) == 1
    approvers, _ = approvers_for_pull_requests[0]
    assert len(approvers) == 0
