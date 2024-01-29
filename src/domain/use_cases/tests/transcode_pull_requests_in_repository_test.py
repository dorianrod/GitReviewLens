import pytest

from src.domain.entities.pull_request import PullRequest
from src.domain.entities.transcoder import Transcoder
from src.domain.use_cases.transcode_pull_requests_in_repository import (
    TranscodePullRequestsInRepositoryUsecase,
)
from src.infra.repositories.in_memory.pull_requests import (
    PullRequestsInMemoryRepository,
)


@pytest.fixture
def use_case(mock_logger, fixture_pull_request_dict):
    return TranscodePullRequestsInRepositoryUsecase(
        logger=mock_logger,
        repository=PullRequestsInMemoryRepository(
            logger=mock_logger,
            git_repository=fixture_pull_request_dict["git_repository"],
        ),
        transcoder=Transcoder("test", {"feat": "feature"}),
    )


def test_it_transcodes_pull_requests_in_repository(fixture_pull_request_dict, use_case):
    pull_request = PullRequest.from_dict(fixture_pull_request_dict)
    repository = use_case.repository

    repository.create(pull_request)

    use_case.execute()

    transcoded_pull_request = repository.get_by_id(pull_request.id)
    assert transcoded_pull_request.type == "feature"
    assert pull_request.type != transcoded_pull_request.type
