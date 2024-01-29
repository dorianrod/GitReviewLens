from dataclasses import dataclass
from typing import Sequence

from src.app.controllers.base_controller import BaseController
from src.app.utils.monitor import monitor
from src.common.monitoring.logger import LoggerInterface
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

    def load_from_repository(self, git_repository, options=None):
        remote_repositories = get_repositories_for_git_repository(git_repository)

        RemoteCommentRepository = remote_repositories["comments"]
        RemotePullRequestRepository = remote_repositories["pull_requests"]

        target_repository = PullRequestsDatabaseRepository(
            logger=self.logger, git_repository=git_repository
        )

        # Only load new pull requests if there is no options
        pull_requests = target_repository.find_all()
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

        pull_requests = usecase.execute(options)

        return pull_requests

    @monitor("Loading pull requests from remote origin")
    def execute(self, options=None):
        branches = settings.get_branches()
        for branch in branches:
            self.load_from_repository(git_repository=branch.repository, options=options)
