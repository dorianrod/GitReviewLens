import pytest
import requests_mock

from src.infra.repositories.azure.pull_requests import PullRequestsAzureRepository


@pytest.fixture
def repository(mock_logger):
    return PullRequestsAzureRepository(
        logger=mock_logger,
        git_repository={
            "project": "testproject",
            "name": "myrepo",
            "organisation": "orga",
        },
    )


async def test_does_not_create_active_pull_requests(
    mocker,
    repository,
    mock_active_pull_request_in_azure,
):
    with requests_mock.Mocker() as mocker:
        mocker.get(
            "https://dev.azure.com/orga/testproject/_apis/git/repositories/myrepo/pullRequests?searchCriteria.status=all&$top=1000&$skip=0",
            json={"value": [mock_active_pull_request_in_azure]},
        )

        pull_requests = await repository.find_all()

        assert len(pull_requests) == 0


async def test_does_create_completed_pull_requests(
    mocker,
    repository,
    mock_completed_pull_request_in_azure,
):
    with requests_mock.Mocker() as mocker:
        mocker.get(
            "https://dev.azure.com/orga/testproject/_apis/git/repositories/myrepo/pullRequests?searchCriteria.status=all&$top=1000&$skip=0",
            json={"value": [mock_completed_pull_request_in_azure]},
        )

        pull_requests = await repository.find_all()

        assert len(pull_requests) == 1
        assert pull_requests[0].to_dict() == {
            "source_id": "2",
            "approvers": [
                {
                    "full_name": "Developer 2",
                    "email": "developer2@org.com",
                    "id": "developer2@org.com",
                }
            ],
            "type": "feature",
            "git_repository": "orga/testproject/myrepo",
            "comments": [],
            "created_by": {
                "full_name": "Developer 1",
                "email": "developer1@org.com",
                "id": "developer1@org.com",
            },
            "title": "fix: ultra priority",
            "creation_date": "2023-10-16T17:14:08Z",
            "completion_date": "2023-10-17T17:14:08Z",
            "merge_time": 540.0,
            "first_comment_delay": None,
            "source_branch": "feat/add-button",
            "target_branch": "master",
            "previous_commit": "8404787b56000382efe2470506c9d3d174ae306c",
            "commit": "129d8cc954433cd62789076de4068701d54ce8ee",
        }


async def test_does_use_pagination(
    mocker,
    mock_completed_pull_request_in_azure,
    mock_completed_pull_request_2_in_azure,
    repository,
):
    with requests_mock.Mocker() as mocker:
        mocker.get(
            "https://dev.azure.com/orga/testproject/_apis/git/repositories/myrepo/pullRequests?searchCriteria.status=all&$top=1&$skip=0",
            json={"value": [mock_completed_pull_request_in_azure]},
        )
        mocker.get(
            "https://dev.azure.com/orga/testproject/_apis/git/repositories/myrepo/pullRequests?searchCriteria.status=all&$top=1&$skip=1",
            json={"value": [mock_completed_pull_request_2_in_azure]},
        )
        mocker.get(
            "https://dev.azure.com/orga/testproject/_apis/git/repositories/myrepo/pullRequests?searchCriteria.status=all&$top=1&$skip=2",
            json={"value": []},
        )

        repository.max_results = 1
        pull_requests = await repository.find_all()

        assert len(pull_requests) == 2


async def test_stops_using_pagination_with_dates(
    mocker,
    mock_completed_pull_request_in_azure,
    repository,
):
    with requests_mock.Mocker() as mocker:
        mocker.get(
            "https://dev.azure.com/orga/testproject/_apis/git/repositories/myrepo/pullRequests?searchCriteria.status=all&$top=1&$skip=0",
            json={"value": [mock_completed_pull_request_in_azure]},
        )

        repository.max_results = 1
        pull_requests = await repository.find_all(
            {
                "end_date": "2023-10-15",
            }
        )

        assert len(pull_requests) == 0


async def test_filters_out_pull_requests_with_date_before_start_date(
    mocker,
    mock_completed_pull_request_in_azure,
    repository,
):
    with requests_mock.Mocker() as mocker:
        mocker.get(
            "https://dev.azure.com/orga/testproject/_apis/git/repositories/myrepo/pullRequests?searchCriteria.status=all&$top=1000&$skip=0",
            json={"value": [mock_completed_pull_request_in_azure]},
        )

        pull_requests = await repository.find_all(
            {
                "start_date": "2024-10-15",
            }
        )

        assert len(pull_requests) == 0


async def test_filters_out_pull_requests_with_date_after_end_date(
    mocker,
    mock_completed_pull_request_in_azure,
    repository,
):
    with requests_mock.Mocker() as mocker:
        mocker.get(
            "https://dev.azure.com/orga/testproject/_apis/git/repositories/myrepo/pullRequests?searchCriteria.status=all&$top=1000&$skip=0",
            json={"value": [mock_completed_pull_request_in_azure]},
        )

        pull_requests = await repository.find_all(
            {
                "end_date": "2020-10-15",
            }
        )

        assert len(pull_requests) == 0


async def test_filters_in_pull_requests_with_startdate_and_enddate(
    mocker,
    mock_completed_pull_request_in_azure,
    repository,
):
    with requests_mock.Mocker() as mocker:
        mocker.get(
            "https://dev.azure.com/orga/testproject/_apis/git/repositories/myrepo/pullRequests?searchCriteria.status=all&$top=1000&$skip=0",
            json={"value": [mock_completed_pull_request_in_azure]},
        )

        pull_requests = await repository.find_all(
            {
                "start_date": "2020-10-15",
                "end_date": "2025-10-15",
            }
        )

        assert len(pull_requests) == 1


async def test_filters_out_pull_requests_with_exclude_filter(
    mocker,
    mock_completed_pull_request_in_azure,
    repository,
):
    with requests_mock.Mocker() as mocker:
        mocker.get(
            "https://dev.azure.com/orga/testproject/_apis/git/repositories/myrepo/pullRequests?searchCriteria.status=all&$top=1000&$skip=0",
            json={"value": [mock_completed_pull_request_in_azure]},
        )

        pull_requests = await repository.find_all(
            {
                "exclude_ids": [mock_completed_pull_request_in_azure["pullRequestId"]],
            }
        )

        assert len(pull_requests) == 0
