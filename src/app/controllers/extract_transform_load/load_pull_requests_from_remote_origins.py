from dataclasses import dataclass
from typing import Sequence

from src.app.controllers.base_controller import BaseController
from src.app.utils.monitor import monitor
from src.common.monitoring.logger import LoggerInterface
from src.common.utils.worker import concurrency_aio
from src.domain.entities.pull_request import PullRequest
from src.domain.use_cases.transfer_pull_requests_from_repositories import (
    TransferPullRequestsToAnotherRepositoryUseCase,
)
from src.infra.repositories.factory import get_repositories_for_git_repository
from src.infra.repositories.postgresql.comments import CommentsDatabaseRepository
from src.infra.repositories.postgresql.pull_requests import (
    PullRequestsDatabaseRepository,
)
from src.settings import settings


@dataclass
class LoadPullRequestsFromRemoteOriginController(
    BaseController[None, Sequence[PullRequest]]
):
    logger: LoggerInterface

    @concurrency_aio(max_concurrency=5)
    async def load_from_repository(self, git_repository, options):
        remote_repositories = get_repositories_for_git_repository(git_repository)

        RemoteCommentRepository = remote_repositories["comments"]
        RemotePullRequestRepository = remote_repositories["pull_requests"]

        target_repository = PullRequestsDatabaseRepository(
            logger=self.logger, git_repository=git_repository
        )

        # Only load new pull requests if there is no options
        pull_requests = await target_repository.find_all()
        if len(pull_requests) > 0 and options is None:
            max_date = max(
                pull_request.completion_date for pull_request in pull_requests
            )
            options = {"start_date": max_date}

        usecase = TransferPullRequestsToAnotherRepositoryUseCase(
            logger=self.logger,
            comments_source_repository=RemoteCommentRepository(
                logger=self.logger, git_repository=git_repository
            ),
            comments_target_repository=CommentsDatabaseRepository(
                logger=self.logger, git_repository=git_repository
            ),
            pull_requests_source_repository=RemotePullRequestRepository(
                logger=self.logger, git_repository=git_repository
            ),
            pull_requests_target_repository=target_repository,
        )

        pull_requests = await usecase.execute(options)

        return pull_requests

    @monitor("Loading pull requests from remote origin")
    async def execute(self, options=None):
        branches = settings.get_branches()

        tasks = [(branch.repository, options) for branch in branches]
        result = self.load_from_repository.run_all(self, tasks)
        return await result
