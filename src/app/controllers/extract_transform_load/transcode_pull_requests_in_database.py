from dataclasses import dataclass

from src.app.controllers.base_controller import BaseController
from src.app.utils.monitor import monitor
from src.common.monitoring.logger import LoggerInterface
from src.domain.use_cases.transcode_pull_requests_in_repository import (
    TranscodePullRequestsInRepositoryUsecase,
)
from src.infra.repositories.json.transcoders import TranscodersJsonRepository
from src.infra.repositories.postgresql.pull_requests import (
    PullRequestsDatabaseRepository,
)
from src.settings import settings


@dataclass
class TranscodePullRequestsInDatabaseController(BaseController[None, None]):
    logger: LoggerInterface
    path: str = "/transco/transcoders.json"

    @monitor("Transcoding pull requests into database")
    def execute(self, *args):
        transcoder = TranscodersJsonRepository(
            logger=self.logger, path=self.path
        ).get_by_id("pull_requests_type")

        branches = settings.get_branches()
        for branch in branches:
            self.logger.info("Transcoding pull requests in " + str(branch.repository))

            repository = PullRequestsDatabaseRepository(
                logger=self.logger, git_repository=branch.repository
            )

            usecase = TranscodePullRequestsInRepositoryUsecase(
                logger=self.logger, repository=repository, transcoder=transcoder
            )

            usecase.execute()
