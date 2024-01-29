from typing import Sequence

from src.app.controllers.base_controller import BaseController
from src.app.utils.monitor import monitor
from src.common.monitoring.logger import LoggerInterface
from src.domain.entities.feature import Feature
from src.domain.entities.repository import Repository
from src.domain.use_cases.get_all import GetAllUseCase
from src.infra.repositories.postgresql.features import FeaturesDatabaseRepository


class GetFeaturesController(BaseController[None, Sequence[Feature]]):
    logger: LoggerInterface
    git_repository: Repository

    def __init__(
        self, logger: LoggerInterface, git_repository: str | dict | Repository
    ):
        self.logger = logger
        self.git_repository = Repository.parse(git_repository)

    @monitor("Getting features")
    def execute(self) -> Sequence[Feature]:
        repository = FeaturesDatabaseRepository(
            logger=self.logger, git_repository=self.git_repository
        )
        return GetAllUseCase(repository=repository).execute()
