from typing import Sequence

from src.domain.entities.pull_request import PullRequest
from src.domain.repositories.pull_requests import PullRequestsRepository
from src.domain.use_cases.get_all import GetAllUseCase


def test_get_all(fixture_pull_request_dict, mock_logger):
    pull_request = PullRequest.from_dict(fixture_pull_request_dict)

    class TestPullRequestsRepository(PullRequestsRepository):
        def find_all(self, options=None) -> Sequence[PullRequest]:
            return [pull_request]

    pull_requests = GetAllUseCase(  # type: ignore
        repository=TestPullRequestsRepository(
            logger=mock_logger, git_repository="orga/repo"
        )
    ).execute()

    assert pull_requests == [pull_request]
