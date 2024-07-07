from dataclasses import dataclass

from src.common.monitoring.logger import LoggerInterface
from src.common.use_cases.base_use_case import BaseUseCase
from src.domain.entities.transcoder import Transcoder
from src.domain.repositories.pull_requests import PullRequestsRepository
from src.domain.use_cases.transcode_pull_requests import TranscodePullRequestsUseCase


@dataclass
class TranscodePullRequestsInRepositoryUsecase(BaseUseCase[None]):
    logger: LoggerInterface
    repository: PullRequestsRepository
    transcoder: Transcoder

    async def execute(self):
        repository = self.repository
        pull_requests = await repository.find_all()
        transcoder_usecase = TranscodePullRequestsUseCase(
            logger=self.logger, transcoder=self.transcoder
        )
        transcoded_pull_requests = await transcoder_usecase.execute(pull_requests)

        nb_updated = 0
        for i in range(len(transcoded_pull_requests)):
            if transcoded_pull_requests[i].type != pull_requests[i].type:
                nb_updated += 1
                await repository.update(
                    transcoded_pull_requests[i],
                    {"upsert_comments": False, "upsert_developers": False},
                )

        self.logger.info("Updated " + str(nb_updated) + " pull requests")
