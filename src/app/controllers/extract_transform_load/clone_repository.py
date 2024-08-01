from dataclasses import dataclass

from src.app.controllers.base_controller import BaseController
from src.app.utils.monitor import monitor
from src.common.monitoring.logger import LoggerInterface
from src.common.settings import settings
from src.common.utils.worker import concurrency_aio
from src.infra.repositories.git.repositories import GitRepoLocal


@dataclass
class CloneRepositoriesController(BaseController[None, None]):
    logger: LoggerInterface

    @concurrency_aio(max_concurrency=5)
    async def clone_repository(self, repository):
        self.logger.info(f"Cloning repository {repository.name}...")
        GitRepoLocal(logger=self.logger).clone(repository.url, repository.name)

    @monitor("Cloning repositories")
    async def execute(self):
        branches = settings.get_branches()
        repositories = [branch.repository for branch in branches]
        await self.clone_repository.run_all(self, repositories)
