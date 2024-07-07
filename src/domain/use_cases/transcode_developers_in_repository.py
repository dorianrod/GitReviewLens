from dataclasses import dataclass

from src.common.monitoring.logger import LoggerInterface
from src.common.use_cases.base_use_case import BaseUseCase
from src.domain.entities.transcoder import Transcoder
from src.domain.repositories.developers import DeveloperRepository
from src.domain.use_cases.transcode_developers import TranscodeDevelopersUseCase


@dataclass
class TranscodeDevelopersInRepositoryUseCase(BaseUseCase[None]):
    logger: LoggerInterface
    repository: DeveloperRepository
    transcoder: Transcoder

    async def execute(self):
        developers = await self.repository.find_all()
        transcoder = TranscodeDevelopersUseCase(
            logger=self.logger, transcoder=self.transcoder
        )
        transcoded_developers = await transcoder.execute(developers)

        developers_to_update = []
        for i in range(len(transcoded_developers)):
            if transcoded_developers[i].full_name != developers[i].full_name:
                developers_to_update.append(transcoded_developers[i])

        await self.repository.update_all(
            developers_to_update,
        )

        self.logger.info("Updated " + str(len(developers_to_update)) + " developers")
