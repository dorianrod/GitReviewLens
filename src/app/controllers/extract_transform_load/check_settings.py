from dataclasses import dataclass
from datetime import datetime

from src.app.controllers.base_controller import BaseController
from src.app.controllers.extract_transform_load.clone_repository import (
    CloneRepositoriesController,
)
from src.app.utils.monitor import monitor
from src.common.monitoring.logger import LoggerInterface
from src.common.utils.date import parse_date
from src.domain.entities.types import RepositoryTypes
from src.domain.repositories.pull_requests import PullRequestsRepository
from src.infra.monitoring.logger import MutedLogger
from src.infra.repositories.azure.pull_requests import PullRequestsAzureRepository
from src.infra.repositories.github.pull_requests import PullRequestsGithubRepository
from src.settings import settings


@dataclass
class CheckSettings(BaseController[None, None]):
    logger: LoggerInterface

    @monitor("Checking settings")
    async def execute(self):
        error = False
        branches = settings.get_branches()

        for branch in branches:
            repository = branch.repository
            self.logger.info(
                f"Checking repository configuration type: {repository.type}..."
            )

            options = {
                "logger": self.logger,
                "git_repository": repository,
            }

            remote_repository: PullRequestsRepository

            if repository.type == RepositoryTypes.AZURE:
                remote_repository = PullRequestsAzureRepository(**options)
            elif repository.type == RepositoryTypes.GITHUB:
                remote_repository = PullRequestsGithubRepository(**options)  # type: ignore
            else:
                self.logger.error(f"Repository type for {repository} is unknown")
                error = True

            try:
                await remote_repository.find_all(
                    {
                        "start_date": parse_date(datetime.now()),
                        "end_date": parse_date(datetime.now()),
                    }  # type: ignore
                )
                self.logger.info(
                    f"Azure configuration for repository ({repository}) is OK"
                )
            except Exception as e:
                self.logger.error(
                    f"Azure configuration for repository ({repository}) is incorrect: {str(e)}"
                )
                error = True

        try:
            self.logger.info("Cloning repositories...")
            await CloneRepositoriesController(logger=MutedLogger()).execute()
            self.logger.info("Repositories cloned successfully")
        except Exception as e:
            self.logger.error(f"Unable to clone some repositories: {str(e)}")
            error = True

        if error:
            raise Exception("THERE WERE SOME ERRORS, PLEASE CHECKS ERROR MESSAGES!")
        else:
            self.logger.info("EVERYTHING IS OK!")
