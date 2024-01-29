from dataclasses import dataclass
from typing import Optional, Sequence, cast

from src.common.monitoring.logger import LoggerInterface
from src.common.use_cases.base_use_case import BaseUseCaseWithParameters
from src.domain.entities.pull_request import PullRequest
from src.domain.repositories.comments import CommentsRepository
from src.domain.repositories.pull_requests import (
    PullRequestsFilters,
    PullRequestsRepository,
)


@dataclass
class TransferPullRequestsToAnotherRepositoryUseCase(
    BaseUseCaseWithParameters[Sequence[PullRequest]]
):
    pull_requests_source_repository: PullRequestsRepository
    comments_source_repository: CommentsRepository

    pull_requests_target_repository: PullRequestsRepository
    comments_target_repository: CommentsRepository

    logger: LoggerInterface

    def execute(
        self,
        options: Optional[PullRequestsFilters] = None,
    ) -> list[PullRequest]:
        self.logger.info(
            f"Creating pull requests to {self.pull_requests_source_repository.__class__.__name__}..."
        )

        options_filters = cast(
            PullRequestsFilters,
            {
                **(options or {}),
            },
        )
        pull_requests_from_source = self.pull_requests_source_repository.find_all(
            options_filters
        )

        self.logger.info(
            f"Creating comments for {len(pull_requests_from_source)} pull requests from {self.comments_source_repository.__class__.__name__} to {self.comments_target_repository.__class__.__name__}..."
        )
        pull_requests: list[PullRequest] = []
        for pull_request in pull_requests_from_source:
            pull_request.comments = []
            self.pull_requests_target_repository.upsert(
                pull_request, {"upset_comments": False}
            )

            comments = self.comments_source_repository.find_all(
                {"pull_request": pull_request}
            )
            for comment in comments:
                self.comments_target_repository.upsert(
                    comment, {"pull_request": pull_request}
                )

            pull_requests.append(pull_request)

            # To update first delay comments
            self.pull_requests_target_repository.upsert(
                pull_request, {"upset_comments": False}
            )

        return pull_requests
