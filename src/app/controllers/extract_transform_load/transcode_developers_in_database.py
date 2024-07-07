from dataclasses import dataclass

from src.app.controllers.base_controller import BaseController
from src.app.utils.monitor import monitor
from src.common.monitoring.logger import LoggerInterface
from src.domain.use_cases.transcode_developers_in_repository import (
    TranscodeDevelopersInRepositoryUseCase,
)
from src.infra.repositories.json.transcoders import TranscodersJsonRepository
from src.infra.repositories.postgresql.developers import DeveloperDatabaseRepository


@dataclass
class TranscodeDevelopersInDatabaseController(BaseController[None, None]):
    logger: LoggerInterface
    path: str = "/transco/transcoders.json"

    @monitor("Transcoding developers into database")
    async def execute(self):
        repository = DeveloperDatabaseRepository(logger=self.logger)

        transcoder = await TranscodersJsonRepository(
            logger=self.logger, path=self.path
        ).get_by_id("developers_names_by_email")

        usecase = TranscodeDevelopersInRepositoryUseCase(
            logger=self.logger, repository=repository, transcoder=transcoder
        )

        await usecase.execute()
