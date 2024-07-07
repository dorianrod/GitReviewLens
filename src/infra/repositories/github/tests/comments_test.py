import pytest
import requests_mock

from src.domain.entities.pull_request import PullRequest
from src.infra.repositories.github.comments import CommentsGithubRepository


@pytest.fixture
def repository(mock_logger):
    return CommentsGithubRepository(
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
    mocker, mock_pull_request_user_comment_in_github, repository, pull_request
):
    with requests_mock.Mocker() as mocker:
        mocker.get(
            f"https://api.github.com/repos/orga/myrepo/pulls/{pull_request.source_id}/comments?per_page=100&page=1",
            json=[mock_pull_request_user_comment_in_github],
        )

        comments = await repository.find_all({"pull_request": pull_request})

        assert len(comments) == 1
        assert comments[0].to_dict() == {
            'id': 'e78ee796779ea493cdbbd75320401da89ce13456dd256c9e6ddc24ba373dd050',
            "content": "Great stuff!",
            "creation_date": "2011-04-14T16:00:49Z",
            "developer": {
                "full_name": "octocat",
                "email": "octocat@github.com",
            },
            "size": 12,
        }


async def test_does_use_pagination(
    mocker,
    mock_pull_request_user_comment_in_github,
    mock_pull_request_user_comment_2_in_github,
    repository,
    pull_request,
):
    with requests_mock.Mocker() as mocker:
        mocker.get(
            f"https://api.github.com/repos/orga/myrepo/pulls/{pull_request.source_id}/comments?per_page=1&page=1",
            json=[mock_pull_request_user_comment_in_github],
        )
        mocker.get(
            f"https://api.github.com/repos/orga/myrepo/pulls/{pull_request.source_id}/comments?per_page=1&page=2",
            json=[mock_pull_request_user_comment_2_in_github],
        )
        mocker.get(
            f"https://api.github.com/repos/orga/myrepo/pulls/{pull_request.source_id}/comments?per_page=1&page=3",
            json=[],
        )

        repository.max_results = 1
        pull_requests = await repository.find_all(
            filters={"pull_request": pull_request}
        )

        assert len(pull_requests) == 2


async def test_does_filter_authors(
    mocker,
    mock_pull_request_user_comment_in_github,
    mock_pull_request_user_comment_2_in_github,
    repository,
    pull_request,
):
    with requests_mock.Mocker() as mocker:
        mocker.get(
            f"https://api.github.com/repos/orga/myrepo/pulls/{pull_request.source_id}/comments?per_page=100&page=1",
            json=[
                mock_pull_request_user_comment_in_github,
                mock_pull_request_user_comment_2_in_github,
            ],
        )

        pull_requests = await repository.find_all(
            filters={"pull_request": pull_request, "authors_to_exclude": ["dupont"]}
        )

        assert len(pull_requests) == 1
