import asyncio
from dataclasses import dataclass
from datetime import datetime

from src.app.controllers.base_controller import BaseController
from src.app.utils.monitor import monitor
from src.common.monitoring.logger import LoggerInterface
from src.infra.repositories.json.developers import DevelopersJsonRepository
from src.infra.repositories.json.features import FeaturesJsonRepository
from src.infra.repositories.json.pull_requests import PullRequestsJsonRepository
from src.infra.repositories.postgresql.developers import DeveloperDatabaseRepository
from src.infra.repositories.postgresql.features import FeaturesDatabaseRepository
from src.infra.repositories.postgresql.pull_requests import (
    PullRequestsDatabaseRepository,
)
from src.settings import settings


@dataclass
class DumpDatabaseController(BaseController[None, None]):
    logger: LoggerInterface
    path: str = "/data"

    @monitor("extracting pull_requests")
    async def extract_pull_requests(self, backup_date, git_repository):
        json_repository_pull_request = PullRequestsJsonRepository(
            logger=self.logger,
            path=f"{self.path}/pull_requests.json",
            git_repository=git_repository,
        )
        db_repository_pull_requests = PullRequestsDatabaseRepository(
            logger=self.logger, git_repository=git_repository
        )

        self.logger.info("Making backup for pull_requests...")
        previous_json_pull_requests = await json_repository_pull_request.find_all()
        await PullRequestsJsonRepository(
            logger=self.logger,
            path=f"{self.path}/{backup_date}/pull_requests.json",
            git_repository=git_repository,
        ).upsert_all(previous_json_pull_requests)

        self.logger.info("Extracting pull_requests from database...")
        pull_requests = await db_repository_pull_requests.find_all()
        await json_repository_pull_request.upsert_all(pull_requests)
        self.logger.info(f"Saved {len(pull_requests)} pull requests")

    @monitor("extracting developers")
    async def extract_developers(self, backup_date, git_repository):
        json_repository_developers = DevelopersJsonRepository(
            logger=self.logger, path=f"{self.path}/developers.json"
        )
        db_repository_developers = DeveloperDatabaseRepository(logger=self.logger)

        self.logger.info("Making backup for developers...")
        previous_json_developers = await json_repository_developers.find_all()
        await DevelopersJsonRepository(
            logger=self.logger,
            path=f"{self.path}/{backup_date}/developers.json",
        ).upsert_all(previous_json_developers)

        self.logger.info("Extracting developers from database...")
        developers = await db_repository_developers.find_all()
        await json_repository_developers.upsert_all(developers)
        self.logger.info(f"Saved {len(developers)} developers")

    @monitor("extracting features")
    async def extract_features(self, backup_date, git_repository):
        json_repository_features = FeaturesJsonRepository(
            logger=self.logger,
            path=f"{self.path}/features.json",
            git_repository=git_repository,
        )
        db_repository_features = FeaturesDatabaseRepository(
            logger=self.logger, git_repository=git_repository
        )

        self.logger.info("Making backup for features...")
        previous_json_features = await json_repository_features.find_all()
        await FeaturesJsonRepository(
            logger=self.logger,
            path=f"{self.path}/{backup_date}/features.json",
            git_repository=git_repository,
        ).upsert_all(previous_json_features)

        self.logger.info("Extracting features from database...")
        features = await db_repository_features.find_all()
        await json_repository_features.upsert_all(features)
        self.logger.info(f"Saved {len(features)} features")

    @monitor("dumping database")
    async def execute(self):
        branches = settings.get_branches()

        tasks = []
        for branch in branches:
            git_repository = branch.repository

            current_date = datetime.now().isoformat()

            tasks.append(self.extract_pull_requests(current_date, git_repository))
            tasks.append(self.extract_developers(current_date, git_repository))
            tasks.append(self.extract_features(current_date, git_repository))

        await asyncio.gather(*tasks)
