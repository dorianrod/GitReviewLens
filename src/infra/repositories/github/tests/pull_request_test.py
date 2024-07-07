import pytest
import requests_mock

from src.infra.repositories.github.pull_requests import PullRequestsGithubRepository


@pytest.fixture
def repository(mock_logger):
    return PullRequestsGithubRepository(
        logger=mock_logger,
        git_repository={
            "name": "myrepo",
            "organisation": "orga",
        },
    )


async def test_does_not_create_active_pull_requests(
    mocker,
    repository,
    mock_active_pull_request_in_github,
):
    with requests_mock.Mocker() as mocker:
        mocker.get(
            "https://api.github.com/repos/orga/myrepo/pulls?state=closed&per_page=100&page=1",
            json=[mock_active_pull_request_in_github],
        )

        pull_requests = await repository.find_all()

        assert len(pull_requests) == 0


async def test_does_create_completed_pull_requests(
    mocker, repository, mock_completed_pull_request_in_github, mock_approvers_in_github
):
    with requests_mock.Mocker() as mocker:
        mocker.get(
            "https://api.github.com/repos/orga/myrepo/pulls?state=closed&per_page=100&page=1",
            json=[mock_completed_pull_request_in_github],
        )

        mocker.get(
            "https://api.github.com/repos/orga/myrepo/pulls/1234/reviews?per_page=100&page=1",
            json=mock_approvers_in_github,
        )

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
    mocker,
    mock_completed_pull_request_in_github,
    mock_completed_pull_request_2_in_github,
    repository,
):
    with requests_mock.Mocker() as mocker:
        mocker.get(
            "https://api.github.com/repos/orga/myrepo/pulls?state=closed&per_page=1&page=1",
            json=[mock_completed_pull_request_in_github],
        )

        mocker.get(
            "https://api.github.com/repos/orga/myrepo/pulls?state=closed&per_page=1&page=2",
            json=[mock_completed_pull_request_2_in_github],
        )

        mocker.get(
            "https://api.github.com/repos/orga/myrepo/pulls?state=closed&per_page=1&page=3",
            json=[],
        )

        mocker.get(
            "https://api.github.com/repos/orga/myrepo/pulls/1234/reviews?per_page=100&page=1",
            json=[],
        )
        mocker.get(
            "https://api.github.com/repos/orga/myrepo/pulls/789/reviews?per_page=100&page=1",
            json=[],
        )

        repository.max_results = 1
        pull_requests = await repository.find_all()

        assert len(pull_requests) == 2


async def test_stops_using_pagination_with_dates(
    mocker,
    mock_completed_pull_request_in_github,
    repository,
):
    with requests_mock.Mocker() as mocker:
        mocker.get(
            "https://api.github.com/repos/orga/myrepo/pulls?state=closed&per_page=1&page=1",
            json=[mock_completed_pull_request_in_github],
        )

        repository.max_results = 1
        pull_requests = await repository.find_all(
            {
                "end_date": "2010-10-15",
            }
        )

        assert len(pull_requests) == 0


async def test_filters_out_pull_requests_with_date_before_start_date(
    mocker,
    mock_completed_pull_request_in_github,
    repository,
):
    with requests_mock.Mocker() as mocker:
        mocker.get(
            "https://api.github.com/repos/orga/myrepo/pulls?state=closed&per_page=100&page=1",
            json=[mock_completed_pull_request_in_github],
        )
        pull_requests = await repository.find_all(
            {
                "start_date": "2020-10-15",
            }
        )
        assert len(pull_requests) == 0


async def test_filters_out_pull_requests_with_date_after_end_date(
    mocker,
    mock_completed_pull_request_in_github,
    repository,
):
    with requests_mock.Mocker() as mocker:
        mocker.get(
            "https://api.github.com/repos/orga/myrepo/pulls?state=closed&per_page=100&page=1",
            json=[mock_completed_pull_request_in_github],
        )

        pull_requests = await repository.find_all(
            {
                "end_date": "2010-10-15",
            }
        )

        assert len(pull_requests) == 0


async def test_filters_in_pull_requests_with_startdate_and_enddate(
    mocker,
    mock_completed_pull_request_in_github,
    repository,
):
    with requests_mock.Mocker() as mocker:
        mocker.get(
            "https://api.github.com/repos/orga/myrepo/pulls?state=closed&per_page=100&page=1",
            json=[mock_completed_pull_request_in_github],
        )

        mocker.get(
            "https://api.github.com/repos/orga/myrepo/pulls/1234/reviews?per_page=100&page=1",
            json=[],
        )

        pull_requests = await repository.find_all(
            {
                "start_date": "2010-10-15",
                "end_date": "2012-10-15",
            }
        )

        assert len(pull_requests) == 1


async def test_filters_out_pull_requests_with_exclude_filter(
    mocker,
    mock_completed_pull_request_in_github,
    repository,
):
    with requests_mock.Mocker() as mocker:
        mocker.get(
            "https://api.github.com/repos/orga/myrepo/pulls?state=closed&per_page=100&page=1",
            json=[mock_completed_pull_request_in_github],
        )

        pull_requests = await repository.find_all(
            {
                "exclude_ids": [mock_completed_pull_request_in_github["number"]],
            }
        )

        assert len(pull_requests) == 0
