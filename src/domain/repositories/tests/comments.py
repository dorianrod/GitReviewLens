from datetime import datetime

import pytest

from src.common.utils.date import are_dates_equal
from src.domain.entities.comment import Comment
from src.domain.entities.pull_request import PullRequest
from src.domain.entities.repository import Repository
from src.domain.exceptions import RepositoryIncompatibility


def test_it_creates_comment(
    comment_repository,
    fixture_comment_dict,
    fixture_pull_request_dict,
):
    pull_request = PullRequest.from_dict(fixture_pull_request_dict)
    pull_request.comments = []

    comment = Comment.from_dict(fixture_comment_dict)
    comment.creation_date = datetime.now()

    comment_repository.create(comment, {"pull_request": pull_request})

    created_comments = comment_repository.find_all(
        filters={"pull_request": pull_request}
    )
    assert len(created_comments) == 1

    created_comment = created_comments[0]
    assert comment.developer.id == created_comment.developer.id
    assert comment.content == created_comment.content
    assert are_dates_equal(comment.creation_date, created_comment.creation_date)


def test_cannot_create_comment_into_wrong_git_repo(
    comment_repository, fixture_comment_dict, fixture_pull_request_dict, db_session
):
    pull_request = PullRequest.from_dict(fixture_pull_request_dict)
    pull_request.comments = []

    comment = Comment.from_dict(fixture_comment_dict)
    comment.creation_date = datetime.now()

    comment_repository.git_repository = Repository.parse("orga/anotherrepo")

    with pytest.raises(RepositoryIncompatibility):
        comment_repository.create(comment, {"pull_request": pull_request})

    comments = comment_repository.find_all(filters={"pull_request": pull_request})
    assert comments == []


def test_can_create_same_comments_for_different_repo(
    comment_repository,
    comment_repository_2,
    fixture_comment_dict,
    fixture_pull_request_dict,
):
    pull_request = PullRequest.from_dict(fixture_pull_request_dict)
    pull_request_from_another_repo = PullRequest.from_dict(
        {**fixture_pull_request_dict, "git_repository": "orga/anotherrepo"}
    )

    comment = Comment.from_dict(fixture_comment_dict)
    comment_repository.create(comment, {"pull_request": pull_request})
    comment_repository_2.create(
        comment, {"pull_request": pull_request_from_another_repo}
    )

    assert comment_repository.find_all({"pull_request": pull_request}) == [comment]
    assert comment_repository_2.find_all(
        {"pull_request": pull_request_from_another_repo}
    ) == [comment]
