from dataclasses import dataclass

from src.app.controllers.base_controller import BaseController
from src.app.utils.monitor import monitor
from src.common.monitoring.logger import LoggerInterface
from src.infra.database.postgresql.database import drop_db as drop_database
from src.infra.database.postgresql.database import init_db
from src.infra.repositories.json.features import FeaturesJsonRepository
from src.infra.repositories.json.pull_requests import PullRequestsJsonRepository
from src.infra.repositories.postgresql.features import FeaturesDatabaseRepository
from src.infra.repositories.postgresql.pull_requests import (
    PullRequestsDatabaseRepository,
)
from src.settings import settings


@dataclass
class InitDatabaseController(BaseController[None, None]):
    logger: LoggerInterface

    @monitor("initializing database")
    async def execute(
        self,
        load_pull_requests=True,
        load_features=True,
        drop_db=True,
        path="/data",
    ):
        self.logger.info("Droping database...")

        if drop_db:
            drop_database()
            init_db()

        branches = settings.get_branches()
        for branch in branches:
            repository = branch.repository

            if load_pull_requests:
                pull_request_json_repository = PullRequestsJsonRepository(
                    logger=self.logger,
                    path=f"{path}/pull_requests.json",
                    git_repository=repository,
                )
                self.logger.info(
                    f"Loading pull requests from {pull_request_json_repository.path}..."
                )
                pull_requests = await pull_request_json_repository.find_all()

                self.logger.info(
                    f"Loading {len(pull_requests)} pull_requests into database. Please wait..."
                )
                db_pull_request_repository = PullRequestsDatabaseRepository(
                    logger=self.logger, git_repository=repository
                )
                await db_pull_request_repository.upsert_all(
                    pull_requests, {"upsert_comments": True}
                )
                self.logger.info(
                    f"Loaded {len(pull_requests)} pull_requests into database."
                )

            if load_features:
                feature_json_repository = FeaturesJsonRepository(
                    logger=self.logger,
                    path=f"{path}/features.json",
                    git_repository=repository,
                )
                self.logger.info(
                    f"Loading features from {feature_json_repository.path}..."
                )
                features = await feature_json_repository.find_all()
                db_feature_repository = FeaturesDatabaseRepository(
                    logger=self.logger, git_repository=repository
                )
                await db_feature_repository.create_all(features)
                self.logger.info(f"Loaded {len(features)} features into database.")
