from dataclasses import dataclass
from typing import Sequence

from src.app.controllers.base_controller import BaseController
from src.app.utils.monitor import monitor
from src.common.monitoring.logger import LoggerInterface
from src.domain.entities.developer import Developer
from src.domain.use_cases.get_all import GetAllUseCase
from src.infra.repositories.postgresql.developers import DeveloperDatabaseRepository


@dataclass
class GetDevelopersController(BaseController[None, Sequence[Developer]]):
    logger: LoggerInterface

    @monitor("Getting developers from database")
    async def execute(self) -> Sequence[Developer]:
        repository = DeveloperDatabaseRepository(logger=self.logger)
        return await GetAllUseCase(repository=repository).execute()
