import pytest
import requests_mock

from src.domain.entities.pull_request import PullRequest
from src.infra.repositories.azure.comments import CommentsAzureRepository
from src.infra.repositories.azure.tests.conftest import (
    mock_pull_request_comments_thread,
)


@pytest.fixture
def repository(mock_logger):
    return CommentsAzureRepository(
        logger=mock_logger,
        git_repository={
            "project": "testproject",
            "name": "myrepo",
            "organisation": "orga",
        },
    )


@pytest.fixture
def pull_request(fixture_pull_request_dict):
    return PullRequest.from_dict({**fixture_pull_request_dict, "source_id": "1"})


async def test_does_not_create_system_comment(
    mocker, mock_pull_request_system_comment, pull_request, repository
):
    with requests_mock.Mocker() as mocker:
        mocker.get(
            f"https://dev.azure.com/orga/testproject/_apis/git/repositories/myrepo/pullRequests/{pull_request.source_id}/threads",
            json={
                "value": [
                    mock_pull_request_comments_thread(
                        [mock_pull_request_system_comment]
                    ),
                    mock_pull_request_comments_thread(
                        [mock_pull_request_system_comment]
                    ),
                ]
            },
        )

        comments = await repository.find_all(filters={"pull_request": pull_request})

        assert len(comments) == 0


async def test_does_get_user_comment_from_several_threads(
    mocker,
    mock_pull_request_user_comment,
    mock_pull_request_user_2_comment,
    repository,
    pull_request,
):
    with requests_mock.Mocker() as mocker:
        mocker.get(
            f"https://dev.azure.com/orga/testproject/_apis/git/repositories/myrepo/pullRequests/{pull_request.source_id}/threads",
            json={
                "value": [
                    mock_pull_request_comments_thread([mock_pull_request_user_comment]),
                    mock_pull_request_comments_thread(
                        [mock_pull_request_user_2_comment]
                    ),
                ]
            },
        )

        comments = await repository.find_all(filters={"pull_request": pull_request})

        assert len(comments) == 2
        assert comments[0].to_dict() == {
            "id": "6ea88e3848fd2a96984debb2aab4c3b86ee9c134c0c3228e630f7f0fcbabd7a3",
            "content": "This is my first comment",
            "creation_date": "2023-10-09T12:04:49Z",
            "developer": {
                "full_name": "Dorian RODRIGUEZ",
                "email": "dorian.rodriguez@email.com",
            },
            "size": 24,
        }
        assert comments[1].to_dict() == {
            'id': 'b43bd984b58782d17f356811b61a4413ab1f601a6b09276e683df0c9ee4dbb61',
            "content": "OK",
            "creation_date": "2024-10-09T12:04:49Z",
            "developer": {
                "full_name": "Juan DOMINGO",
                "email": "juan.domingo@email.com",
            },
            "size": 2,
        }


async def test_does_filters_authors(
    mocker,
    mock_pull_request_user_comment,
    repository,
    pull_request,
):
    with requests_mock.Mocker() as mocker:
        mocker.get(
            f"https://dev.azure.com/orga/testproject/_apis/git/repositories/myrepo/pullRequests/{pull_request.source_id}/threads",
            json={
                "value": [
                    mock_pull_request_comments_thread([mock_pull_request_user_comment]),
                ]
            },
        )

        comments = await repository.find_all(
            filters={
                "pull_request": pull_request,
                "authors_to_exclude": ["Dorian RODRIGUEZ"],
            }
        )

        assert len(comments) == 0
