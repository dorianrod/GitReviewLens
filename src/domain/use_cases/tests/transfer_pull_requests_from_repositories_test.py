import pytest

from src.domain.entities.comment import Comment
from src.domain.entities.pull_request import PullRequest
from src.domain.use_cases.transfer_pull_requests_from_repositories import (
    TransferPullRequestsToAnotherRepositoryUseCase,
)
from src.infra.repositories.in_memory.pull_requests import (
    PullRequestsInMemoryRepository,
)


@pytest.fixture
def init_use_case(mock_logger, fixture_pull_request_dict):
    source_repository = PullRequestsInMemoryRepository(
        logger=mock_logger,
        git_repository=fixture_pull_request_dict["git_repository"],
    )
    target_repository = PullRequestsInMemoryRepository(
        logger=mock_logger,
        git_repository=fixture_pull_request_dict["git_repository"],
    )
    use_case = TransferPullRequestsToAnotherRepositoryUseCase(
        logger=mock_logger,
        source_repository=source_repository,
        target_repository=target_repository,
    )

    return (
        use_case,
        source_repository,
        target_repository,
    )


async def test_creates_pull_requests_and_comments(
    init_use_case, fixture_pull_request_dict
):
    (
        use_case,
        source_repository,
        target_repository,
    ) = init_use_case

    pull_request = PullRequest.from_dict(
        {
            **fixture_pull_request_dict,
            "comments": [fixture_pull_request_dict["comments"][0]],
        }
    )
    pull_request_2 = PullRequest.from_dict(
        {
            **fixture_pull_request_dict,
            "source_id": "200",
            "comments": [fixture_pull_request_dict["comments"][0]],
        }
    )

    await source_repository.upsert_all([pull_request, pull_request_2])

    pull_requests = await use_case.execute()
    assert len(pull_requests) == 2

    pull_requests = sorted(pull_requests, key=lambda pr: pr.source_id)

    assert pull_requests[0] == pull_request
    assert pull_requests[1] == pull_request_2

    saved_pull_requests = await target_repository.find_all()
    assert sorted(saved_pull_requests, key=lambda pr: pr.source_id) == sorted(
        [
            pull_request,
            pull_request_2,
        ],
        key=lambda pr: pr.source_id,
    )


async def test_update_pull_requests_that_exist_yet(
    init_use_case, fixture_pull_request_dict
):
    (
        use_case,
        source_repository,
        target_repository,
    ) = init_use_case

    target_pull_request = PullRequest.from_dict(
        {**fixture_pull_request_dict, "comments": []}
    )
    await target_repository.create(target_pull_request)

    source_pull_request = PullRequest.from_dict(
        {
            **fixture_pull_request_dict,
            "title": "changed title",
            "comments": [fixture_pull_request_dict["comments"][0]],
        }
    )
    await source_repository.create(source_pull_request)

    pull_requests = await use_case.execute()
    assert len(pull_requests) == 1
    assert await target_repository.find_all() == [source_pull_request]


async def test_create_or_updates_comments_for_pull_requests_that_exist_yet(
    init_use_case, fixture_pull_request_dict
):
    (
        use_case,
        source_repository,
        target_repository,
    ) = init_use_case

    target_pull_request = PullRequest.from_dict(
        {
            **fixture_pull_request_dict,
            "comments": [fixture_pull_request_dict["comments"][0]],
        }
    )
    await target_repository.create(target_pull_request)

    source_pull_request = PullRequest.from_dict(
        {
            **fixture_pull_request_dict,
            "comments": [
                {**fixture_pull_request_dict["comments"][0], "content": "toto"}
            ],
        }
    )
    await source_repository.create(source_pull_request)

    await use_case.execute()

    updated_pull_requests = await target_repository.find_all()
    assert len(updated_pull_requests) == 1
    assert len(updated_pull_requests[0].comments) == 2
