from dataclasses import dataclass

from src.app.controllers.base_controller import BaseController
from src.app.utils.monitor import monitor
from src.common.monitoring.logger import LoggerInterface
from src.infra.repositories.git.repositories import GitRepoLocal
from src.settings import settings


@dataclass
class CloneRepositoriesController(BaseController[None, None]):
    logger: LoggerInterface

    @monitor("Cloning repositories")
    async def execute(self):
        branches = settings.get_branches()
        for branch in branches:
            repository = branch.repository
            self.logger.info(f"Cloning repository {repository.name}...")
            GitRepoLocal(logger=self.logger).clone(repository.url, repository.name)
