import pytest

from src.infra.repositories.azure.pull_requests import PullRequestsAzureRepository


@pytest.fixture
def repository(mock_logger):
    return PullRequestsAzureRepository(
        pagination={"max_concurrency": 1},
        logger=mock_logger,
        git_repository={
            "project": "testproject",
            "name": "myrepo",
            "organisation": "orga",
        },
    )


@pytest.fixture
def repository_concurrency(mock_logger):
    return PullRequestsAzureRepository(
        pagination={"max_concurrency": 1, "items_per_page": 1},
        logger=mock_logger,
        git_repository={
            "project": "testproject",
            "name": "myrepo",
            "organisation": "orga",
        },
    )


async def test_does_not_create_active_pull_requests(
    repository, mock_active_pull_request_in_azure, mock_api_pull_requests
):
    mock_api_pull_requests([mock_active_pull_request_in_azure])

    pull_requests = await repository.find_all()
    assert len(pull_requests) == 0


async def test_does_create_completed_pull_requests_with_comments(
    repository,
    mock_completed_pull_request_in_azure,
    mock_thread_comments,
    mock_pull_request_user_comment,
    mock_api_pull_requests,
    mock_pull_request_comments_thread,
):

    mock_api_pull_requests([mock_completed_pull_request_in_azure])
    mock_thread_comments(
        mock_completed_pull_request_in_azure["pullRequestId"],
        [mock_pull_request_comments_thread([mock_pull_request_user_comment])],
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
        "comments": [
            {
                "id": "6ea88e3848fd2a96984debb2aab4c3b86ee9c134c0c3228e630f7f0fcbabd7a3",
                "content": "This is my first comment",
                "pull_request_id": "679f53bf8e70acb7db8ad5d93008eea72fbb6b51f2e07c13eb04b02c62073c8e",
                "creation_date": "2023-10-09T12:04:49Z",
                "developer": {
                    "full_name": "Dorian RODRIGUEZ",
                    "email": "dorian.rodriguez@email.com",
                },
                "size": 24,
            }
        ],
        "type": "feature",
        "git_repository": "orga/testproject/myrepo",
        "created_by": {
            "full_name": "Developer 1",
            "email": "developer1@org.com",
            "id": "developer1@org.com",
        },
        "title": "fix: ultra priority",
        "creation_date": "2023-10-16T17:14:08Z",
        "completion_date": "2023-10-17T17:14:08Z",
        "merge_time": 540.0,
        "first_comment_delay": 0,
        "source_branch": "feat/add-button",
        "target_branch": "master",
        "previous_commit": "8404787b56000382efe2470506c9d3d174ae306c",
        "commit": "129d8cc954433cd62789076de4068701d54ce8ee",
    }


async def test_does_use_pagination(
    mock_completed_pull_request_in_azure,
    mock_completed_pull_request_2_in_azure,
    repository_concurrency,
    mock_thread_comments,
    mock_api_pull_requests,
):

    mock_api_pull_requests([mock_completed_pull_request_in_azure], per_page=1, page=1)
    mock_api_pull_requests([mock_completed_pull_request_2_in_azure], per_page=1, page=2)
    mock_api_pull_requests([], per_page=1, page=3)
    mock_thread_comments(
        mock_completed_pull_request_in_azure["pullRequestId"],
        [],
    )
    mock_thread_comments(
        mock_completed_pull_request_2_in_azure["pullRequestId"],
        [],
    )

    pull_requests = await repository_concurrency.find_all()
    assert len(pull_requests) == 2


async def test_stops_using_pagination_with_dates(
    mock_completed_pull_request_in_azure, repository_concurrency, mock_api_pull_requests
):
    mock_api_pull_requests([mock_completed_pull_request_in_azure], per_page=1, page=1)

    pull_requests = await repository_concurrency.find_all(
        {
            "end_date": "2023-10-15",
        }
    )
    assert len(pull_requests) == 0


async def test_filters_out_pull_requests_with_date_before_start_date(
    mock_completed_pull_request_in_azure, repository, mock_api_pull_requests
):
    mock_api_pull_requests([mock_completed_pull_request_in_azure])

    pull_requests = await repository.find_all(
        {
            "start_date": "2024-10-15",
        }
    )
    assert len(pull_requests) == 0


async def test_filters_out_pull_requests_with_date_after_end_date(
    mock_completed_pull_request_in_azure, repository, mock_api_pull_requests
):
    mock_api_pull_requests([mock_completed_pull_request_in_azure])

    pull_requests = await repository.find_all(
        {
            "end_date": "2020-10-15",
        }
    )
    assert len(pull_requests) == 0


async def test_filters_in_pull_requests_with_startdate_and_enddate(
    mock_completed_pull_request_in_azure,
    repository,
    mock_thread_comments,
    mock_api_pull_requests,
):
    mock_api_pull_requests([mock_completed_pull_request_in_azure])

    mock_thread_comments(
        mock_completed_pull_request_in_azure["pullRequestId"],
        [],
    )
    pull_requests = await repository.find_all(
        {
            "start_date": "2020-10-15",
            "end_date": "2025-10-15",
        }
    )
    assert len(pull_requests) == 1


async def test_filters_out_pull_requests_with_exclude_filter(
    mock_completed_pull_request_in_azure, repository, mock_api_pull_requests
):
    mock_api_pull_requests([mock_completed_pull_request_in_azure])

    pull_requests = await repository.find_all(
        {
            "exclude_ids": [mock_completed_pull_request_in_azure["pullRequestId"]],
        }
    )
    assert len(pull_requests) == 0
