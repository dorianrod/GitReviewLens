import asyncio
from dataclasses import dataclass

from src.app.controllers.base_controller import BaseController
from src.app.utils.monitor import monitor
from src.common.monitoring.logger import LoggerInterface
from src.common.settings import settings
from src.common.utils.worker import concurrency_aio
from src.domain.use_cases.transcode_pull_requests_in_repository import (
    TranscodePullRequestsInRepositoryUsecase,
)
from src.infra.repositories.json.transcoders import TranscodersJsonRepository
from src.infra.repositories.postgresql.pull_requests import (
    PullRequestsDatabaseRepository,
)


@dataclass
class TranscodePullRequestsInDatabaseController(BaseController[None, None]):
    logger: LoggerInterface
    path: str = "/transco/transcoders.json"

    @concurrency_aio(max_concurrency=5)
    async def transcode_branch(self, branch, transcoder):
        self.logger.info("Transcoding pull requests in " + str(branch.repository))

        repository = PullRequestsDatabaseRepository(
            logger=self.logger, git_repository=branch.repository
        )

        usecase = TranscodePullRequestsInRepositoryUsecase(
            logger=self.logger, repository=repository, transcoder=transcoder
        )

        await usecase.execute()

    @monitor("Transcoding pull requests into database")
    async def execute(self, *args):
        transcoder = await TranscodersJsonRepository(
            logger=self.logger, path=self.path
        ).get_by_id("pull_requests_type")

        branches = settings.get_branches()
        tasks = [self.transcode_branch(branch, transcoder) for branch in branches]
        await asyncio.gather(*tasks)
