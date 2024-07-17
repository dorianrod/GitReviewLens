from dataclasses import dataclass
from typing import Optional, Sequence

from src.common.monitoring.logger import LoggerInterface
from src.common.use_cases.base_use_case import BaseUseCaseWithParameters
from src.common.utils.worker import concurrency_aio
from src.domain.entities.pull_request import PullRequest
from src.domain.repositories.pull_requests import (
    PullRequestsFilters,
    PullRequestsRepository,
)


@dataclass
class TransferPullRequestsToAnotherRepositoryUseCase(
    BaseUseCaseWithParameters[Sequence[PullRequest]]
):
    source_repository: PullRequestsRepository
    target_repository: PullRequestsRepository

    logger: LoggerInterface

    @concurrency_aio(max_concurrency=5)
    async def transfer_pull_request(self, pull_request):
        await self.target_repository.upsert(
            pull_request, {"upsert_comments": True, "upsert_developers": True}
        )
        self.logger.info(
            f"Transfer pull request {pull_request} with {len(pull_request.comments)} comments"
        )
        return pull_request

    async def execute(
        self,
        options: Optional[PullRequestsFilters] = None,
    ) -> list[PullRequest]:
        options_filters: PullRequestsFilters = options or {}  # type: ignore

        self.logger.info(
            f"Getting pull requests from {self.source_repository.__class__.__name__}..."
        )

        pull_requests_from_source = await self.source_repository.find_all(
            options_filters
        )

        pull_requests: list[PullRequest] = await self.transfer_pull_request.run_all(
            self, pull_requests_from_source
        )

        return pull_requests
