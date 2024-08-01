from dataclasses import dataclass
from typing import Optional

from src.common.monitoring.logger import LoggerInterface
from src.common.use_cases.base_use_case import BaseUseCaseWithParameters
from src.domain.entities.pull_request import PullRequest
from src.domain.repositories.pull_requests import (
    PullRequestsFilters,
    PullRequestsRepository,
)


@dataclass
class TransferPullRequestsToAnotherRepositoryUseCase(
    BaseUseCaseWithParameters[list[PullRequest]]
):
    source_repository: PullRequestsRepository
    target_repository: PullRequestsRepository

    logger: LoggerInterface

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

        await self.target_repository.upsert_all(
            pull_requests_from_source,
            {"upsert_comments": True, "upsert_developers": True},
        )

        return pull_requests_from_source
