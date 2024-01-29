import pytest

from src.domain.entities.comment import Comment
from src.domain.entities.pull_request import PullRequest
from src.domain.use_cases.transfer_pull_requests_from_repositories import (
    TransferPullRequestsToAnotherRepositoryUseCase,
)
from src.infra.repositories.in_memory.comments import CommentsInMemoryRepository
from src.infra.repositories.in_memory.pull_requests import (
    PullRequestsInMemoryRepository,
)


@pytest.fixture
def init_use_case(mock_logger, fixture_pull_request_dict):
    comments_source_repository = CommentsInMemoryRepository(
        logger=mock_logger,
        git_repository=fixture_pull_request_dict["git_repository"],
    )
    comments_target_repository = CommentsInMemoryRepository(
        logger=mock_logger,
        git_repository=fixture_pull_request_dict["git_repository"],
    )

    pull_requests_source_repository = PullRequestsInMemoryRepository(
        logger=mock_logger,
        git_repository=fixture_pull_request_dict["git_repository"],
    )
    pull_requests_target_repository = PullRequestsInMemoryRepository(
        logger=mock_logger,
        git_repository=fixture_pull_request_dict["git_repository"],
    )

    use_case = TransferPullRequestsToAnotherRepositoryUseCase(
        logger=mock_logger,
        comments_source_repository=comments_source_repository,
        comments_target_repository=comments_target_repository,
        pull_requests_source_repository=pull_requests_source_repository,
        pull_requests_target_repository=pull_requests_target_repository,
    )

    return (
        use_case,
        comments_source_repository,
        comments_target_repository,
        pull_requests_source_repository,
        pull_requests_target_repository,
    )


def test_creates_pull_requests_and_comments(init_use_case, fixture_pull_request_dict):
    (
        use_case,
        comments_source_repository,
        comments_target_repository,
        pull_requests_source_repository,
        pull_requests_target_repository,
    ) = init_use_case

    pull_request = PullRequest.from_dict({**fixture_pull_request_dict, "comments": []})
    pull_request_2 = PullRequest.from_dict(
        {**fixture_pull_request_dict, "source_id": "200", "comments": []}
    )

    pull_requests_source_repository.create(pull_request)
    pull_requests_source_repository.create(pull_request_2)

    comment_1 = Comment.from_dict(fixture_pull_request_dict["comments"][0])
    comments_source_repository.create(comment_1, {"pull_request": pull_request})

    comment_2 = Comment.from_dict(fixture_pull_request_dict["comments"][0])
    comments_source_repository.create(comment_2, {"pull_request": pull_request})

    pull_requests = use_case.execute()
    assert len(pull_requests) == 2

    pull_requests = sorted(pull_requests, key=lambda pr: pr.source_id)

    assert pull_requests[0] == pull_request
    assert pull_requests[1] == pull_request_2

    saved_pull_requests = pull_requests_target_repository.find_all()
    assert sorted(saved_pull_requests, key=lambda pr: pr.source_id) == sorted(
        [
            pull_request,
            pull_request_2,
        ],
        key=lambda pr: pr.source_id,
    )


def test_update_pull_requests_that_exist_yet(init_use_case, fixture_pull_request_dict):
    (
        use_case,
        comments_source_repository,
        comments_target_repository,
        pull_requests_source_repository,
        pull_requests_target_repository,
    ) = init_use_case

    target_pull_request = PullRequest.from_dict(
        {**fixture_pull_request_dict, "comments": []}
    )
    pull_requests_target_repository.create(target_pull_request)

    source_pull_request = PullRequest.from_dict(
        {**fixture_pull_request_dict, "title": "changed title", "comments": []}
    )
    pull_requests_source_repository.create(source_pull_request)

    comment = Comment.from_dict(fixture_pull_request_dict["comments"][0])
    comments_source_repository.create(comment, {"pull_request": source_pull_request})

    pull_requests = use_case.execute()
    assert len(pull_requests) == 1
    assert pull_requests_target_repository.find_all() == [source_pull_request]


def test_create_or_updates_comments_for_pull_requests_that_exist_yet(
    init_use_case, fixture_pull_request_dict
):
    (
        use_case,
        comments_source_repository,
        comments_target_repository,
        pull_requests_source_repository,
        pull_requests_target_repository,
    ) = init_use_case

    target_pull_request = PullRequest.from_dict(
        {**fixture_pull_request_dict, "comments": []}
    )
    pull_requests_target_repository.create(target_pull_request)
    comment = Comment.from_dict(fixture_pull_request_dict["comments"][0])
    comments_target_repository.create(comment, {"pull_request": target_pull_request})

    source_pull_request = PullRequest.from_dict(
        {**fixture_pull_request_dict, "comments": []}
    )
    pull_requests_source_repository.create(source_pull_request)

    updated_comment = Comment.from_dict(
        {**fixture_pull_request_dict["comments"][0], "content": "toto"}
    )
    comments_source_repository.create(
        updated_comment, {"pull_request": source_pull_request}
    )

    use_case.execute()

    updated_comments = comments_target_repository.find_all(
        {"pull_request": target_pull_request}
    )
    assert len(updated_comments) == 1
    assert updated_comments[0].content == "toto"
