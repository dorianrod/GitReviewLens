import pytest

from src.infra.repositories.github.approvers import ApproversGithubRepository
from src.infra.repositories.github.comments import CommentsGithubRepository
from src.infra.repositories.github.pull_requests import PullRequestsGithubRepository


@pytest.fixture(autouse=True, scope="function")
def mock_approvers_repository(mocker):
    class ApproversGithubRepositoryMock(ApproversGithubRepository):
        def __init__(
            self,
            git_repository,
            pagination={
                "max_concurrency": 1,
                "items_per_page": 100,
            },
            *args,
            **kwargs,
        ):
            super().__init__(
                git_repository=git_repository, pagination=pagination, *args, **kwargs
            )

    mocker.patch(
        "src.infra.repositories.github.pull_requests.ApproversGithubRepository",
        ApproversGithubRepositoryMock,
    )


@pytest.fixture(autouse=True, scope="function")
def mock_comments_repository(mocker):
    class CommentsGithubRepositoryMock(CommentsGithubRepository):
        def __init__(
            self,
            git_repository,
            pagination={
                "max_concurrency": 1,
                "items_per_page": 100,
            },
            *args,
            **kwargs,
        ):
            super().__init__(
                git_repository=git_repository, pagination=pagination, *args, **kwargs
            )

    mocker.patch(
        "src.infra.repositories.github.pull_requests.CommentsGithubRepository",
        CommentsGithubRepositoryMock,
    )


@pytest.fixture
def repository(mock_logger):
    return PullRequestsGithubRepository(
        pagination={
            "max_concurrency": 1,
            "items_per_page": 100,
        },
        logger=mock_logger,
        git_repository={
            "name": "myrepo",
            "organisation": "orga",
        },
    )


@pytest.fixture
def repository_pagination(mock_logger):
    return PullRequestsGithubRepository(
        pagination={
            "max_concurrency": 1,
            "items_per_page": 1,
        },
        logger=mock_logger,
        git_repository={
            "name": "myrepo",
            "organisation": "orga",
        },
    )


async def test_does_not_create_active_pull_requests(
    repository, mock_active_pull_request_in_github, mock_api_pull_requests
):
    mock_api_pull_requests([mock_active_pull_request_in_github])
    pull_requests = await repository.find_all()
    assert len(pull_requests) == 0


async def test_does_create_completed_pull_requests(
    repository,
    mock_completed_pull_request_in_github,
    mock_approvers_in_github,
    mock_api_pull_requests,
    mock_api_approvers,
    mock_api_comments,
):
    mock_api_pull_requests([mock_completed_pull_request_in_github])
    mock_api_approvers(1234, mock_approvers_in_github)
    mock_api_comments(1234, [])

    pull_requests = await repository.find_all()

    assert len(pull_requests) == 1
    assert pull_requests[0].to_dict() == {
        "source_id": "1234",
        "approvers": [
            {
                'email': 'approveruser@github.com',
                'full_name': 'approveruser',
                'id': 'approveruser@github.com',
            }
        ],
        "comments": [],
        "created_by": {
            "full_name": "octocat",
            "email": "octocat@github.com",
            "id": "octocat@github.com",
        },
        "creation_date": "2011-01-26T12:01:12Z",
        "completion_date": "2011-01-26T12:03:12Z",
        "title": "Amazing new feature",
        "source_branch": "new-topic",
        "target_branch": "master",
        "commit": "e5bd3914e2e596debea16f433f57875b5b90bcd6",
        "previous_commit": "6dcb09b5b57875f334f61aebed695e2e4193db5e",
        "git_repository": "orga/myrepo",
        "type": "feature",
        "merge_time": 2.0,
        "first_comment_delay": None,
    }


async def test_does_use_pagination(
    mock_completed_pull_request_in_github,
    mock_completed_pull_request_2_in_github,
    repository_pagination,
    mock_api_pull_requests,
    mock_api_approvers,
    mock_api_comments,
):
    mock_api_pull_requests([mock_completed_pull_request_in_github], per_page=1, page=1)
    mock_api_pull_requests(
        [mock_completed_pull_request_2_in_github], per_page=1, page=2
    )
    mock_api_pull_requests([], per_page=1, page=3)
    mock_api_approvers(1234, [])
    mock_api_approvers(789, [])
    mock_api_comments(1234, [])
    mock_api_comments(789, [])

    pull_requests = await repository_pagination.find_all()
    assert len(pull_requests) == 2


async def test_stops_using_pagination_with_dates(
    mock_completed_pull_request_in_github,
    repository_pagination,
    mock_api_pull_requests,
):
    mock_api_pull_requests([mock_completed_pull_request_in_github], per_page=1)

    pull_requests = await repository_pagination.find_all(
        {
            "end_date": "2010-10-15",
        }
    )

    assert len(pull_requests) == 0


async def test_filters_out_pull_requests_with_date_before_start_date(
    mock_completed_pull_request_in_github, repository, mock_api_pull_requests
):
    mock_api_pull_requests([mock_completed_pull_request_in_github])
    pull_requests = await repository.find_all(
        {
            "start_date": "2020-10-15",
        }
    )
    assert len(pull_requests) == 0


async def test_filters_out_pull_requests_with_date_after_end_date(
    mock_completed_pull_request_in_github, repository, mock_api_pull_requests
):
    mock_api_pull_requests([mock_completed_pull_request_in_github])
    pull_requests = await repository.find_all(
        {
            "end_date": "2010-10-15",
        }
    )

    assert len(pull_requests) == 0


async def test_filters_in_pull_requests_with_startdate_and_enddate(
    mock_completed_pull_request_in_github,
    repository,
    mock_api_pull_requests,
    mock_api_approvers,
    mock_api_comments,
):
    mock_api_pull_requests([mock_completed_pull_request_in_github])
    mock_api_approvers(1234, [])
    mock_api_comments(1234, [])

    pull_requests = await repository.find_all(
        {
            "start_date": "2010-10-15",
            "end_date": "2012-10-15",
        }
    )

    assert len(pull_requests) == 1


async def test_filters_out_pull_requests_with_exclude_filter(
    mock_completed_pull_request_in_github,
    repository,
    mock_api_pull_requests,
):
    mock_api_pull_requests([mock_completed_pull_request_in_github])

    pull_requests = await repository.find_all(
        {
            "exclude_ids": [mock_completed_pull_request_in_github["number"]],
        }
    )

    assert len(pull_requests) == 0
