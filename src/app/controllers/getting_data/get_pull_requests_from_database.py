from typing import Sequence

from src.app.controllers.base_controller import BaseController
from src.app.utils.monitor import monitor
from src.common.monitoring.logger import LoggerInterface
from src.domain.entities.pull_request import PullRequest
from src.domain.entities.repository import Repository
from src.domain.use_cases.get_all import GetAllUseCase
from src.infra.repositories.postgresql.pull_requests import (
    PullRequestsDatabaseRepository,
)


class GetPullRequestsController(BaseController[None, Sequence[PullRequest]]):
    logger: LoggerInterface
    git_repository: Repository

    def __init__(
        self, logger: LoggerInterface, git_repository: str | dict | Repository
    ):
        self.logger = logger
        self.git_repository = Repository.parse(git_repository)

    @monitor("Getting pull requests")
    def execute(self) -> Sequence[PullRequest]:
        repository = PullRequestsDatabaseRepository(
            logger=self.logger, git_repository=self.git_repository
        )
        return GetAllUseCase(repository=repository).execute()
