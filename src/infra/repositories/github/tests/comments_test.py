import pytest

from src.domain.entities.pull_request import PullRequest
from src.infra.repositories.github.comments import CommentsGithubRepository


@pytest.fixture
def repository(mock_logger):
    return CommentsGithubRepository(
        pagination={"max_concurrency": 1},
        logger=mock_logger,
        git_repository={
            "name": "myrepo",
            "organisation": "orga",
        },
    )


@pytest.fixture
def repository_pagination(mock_logger):
    return CommentsGithubRepository(
        pagination={"max_concurrency": 1, "items_per_page": 1},
        logger=mock_logger,
        git_repository={
            "name": "myrepo",
            "organisation": "orga",
        },
    )


@pytest.fixture
def pull_request(fixture_pull_request_dict):
    return PullRequest.from_dict(
        {**fixture_pull_request_dict, "source_id": "1", "git_repository": "orga/myrepo"}
    )


async def test_does_get_pull_request_comments(
    mock_pull_request_user_comment_in_github,
    repository,
    pull_request,
    mock_api_comments,
):
    mock_api_comments(
        pull_request.source_id, [mock_pull_request_user_comment_in_github]
    )

    comments = await repository.find_all({"pull_requests": [pull_request]})

    assert len(comments) == 1
    assert comments[0].to_dict() == {
        'id': 'e78ee796779ea493cdbbd75320401da89ce13456dd256c9e6ddc24ba373dd050',
        "content": "Great stuff!",
        "pull_request_id": pull_request.id,
        "creation_date": "2011-04-14T16:00:49Z",
        "developer": {
            "full_name": "octocat",
            "email": "octocat@github.com",
        },
        "size": 12,
    }


async def test_does_use_pagination(
    mock_pull_request_user_comment_in_github,
    mock_pull_request_user_comment_2_in_github,
    repository_pagination,
    pull_request,
    mock_api_comments,
):
    mock_api_comments(
        pull_request.source_id,
        [mock_pull_request_user_comment_in_github],
        per_page=1,
        page=1,
    )
    mock_api_comments(
        pull_request.source_id,
        [mock_pull_request_user_comment_2_in_github],
        per_page=1,
        page=2,
    )
    mock_api_comments(
        pull_request.source_id,
        [],
        per_page=1,
        page=3,
    )

    pull_requests = await repository_pagination.find_all(
        {"pull_requests": [pull_request]}
    )

    assert len(pull_requests) == 2


async def test_does_filter_authors(
    mock_pull_request_user_comment_in_github,
    mock_pull_request_user_comment_2_in_github,
    repository,
    pull_request,
    mock_api_comments,
):
    mock_api_comments(
        pull_request.source_id,
        [
            mock_pull_request_user_comment_in_github,
            mock_pull_request_user_comment_2_in_github,
        ],
    )

    pull_requests = await repository.find_all(
        {"pull_requests": [pull_request], "authors_to_exclude": ["dupont"]}
    )

    assert len(pull_requests) == 1
