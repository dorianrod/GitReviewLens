import json
import os
from typing import Optional

from src.app.controllers.base_controller import BaseController
from src.app.utils.monitor import monitor
from src.common.monitoring.logger import LoggerInterface
from src.common.settings import settings
from src.common.utils.env import replace_env_var
from src.common.utils.worker import concurrency_aio
from src.domain.entities.branch import Branch
from src.domain.entities.repository import Repository
from src.domain.factories.repository import RepositoryFactory
from src.domain.use_cases.anonymize_dataset import AnonymizeDatasetUseCase
from src.infra.repositories.json.features import FeaturesJsonRepository
from src.infra.repositories.json.pull_requests import PullRequestsJsonRepository
from src.infra.repositories.postgresql.features import FeaturesDatabaseRepository
from src.infra.repositories.postgresql.pull_requests import (
    PullRequestsDatabaseRepository,
)


class AnonymizeDatabaseDataToJSONController(BaseController[None, None]):
    logger: LoggerInterface
    path: str
    env_file_model: str

    def __init__(
        self,
        logger: LoggerInterface,
        path: Optional[str] = None,
        env_file_model: Optional[str] = None,
        git_repository: Optional[str | Repository] = None,
    ):
        self.logger = logger
        self.git_repository = git_repository or (
            Repository.parse(git_repository) if git_repository else None
        )
        self.path = path or "/anonymized_data"
        self.env_file_model = env_file_model or "/anonymized_data/.env"

    @monitor("anonymizing pull_requests")
    async def anonymize_pull_requests(self, git_repository):
        json_repository_pull_request = PullRequestsJsonRepository(
            logger=self.logger,
            path=f"{self.path}/pull_requests.json",
            git_repository=git_repository,
        )
        db_repository_pull_requests = PullRequestsDatabaseRepository(
            logger=self.logger, git_repository=git_repository
        )

        self.logger.info("Extracting pull_requests from database...")
        pull_requests = await db_repository_pull_requests.find_all()
        await AnonymizeDatasetUseCase(self.logger).execute(pull_requests, [])  # type: ignore

        await json_repository_pull_request.upsert_all(pull_requests)
        self.logger.info(f"Saved {len(pull_requests)} pull requests")

    @monitor("anonymizing features")
    async def anonymize_features(self, git_repository):
        json_repository_features = FeaturesJsonRepository(
            logger=self.logger,
            path=f"{self.path}/features.json",
            git_repository=git_repository,
        )
        db_repository_features = FeaturesDatabaseRepository(
            logger=self.logger, git_repository=git_repository
        )

        self.logger.info("Extracting features from database...")
        features = await db_repository_features.find_all()
        await json_repository_features.upsert_all(features)
        self.logger.info(f"Saved {len(features)} features")

    @concurrency_aio(max_concurrency=5)
    async def anonymize_branch(self, branch, start_date, end_date, i):
        git_repository = branch.repository

        db_repository_pull_requests = PullRequestsDatabaseRepository(
            logger=self.logger, git_repository=git_repository
        )
        db_repository_features = FeaturesDatabaseRepository(
            logger=self.logger, git_repository=git_repository
        )

        self.logger.info("Extracting pull_requests from database...")
        pull_requests = await db_repository_pull_requests.find_all()

        self.logger.info("Extracting features from database...")
        features = await db_repository_features.find_all()

        self.logger.info("Anonymizing features and pull requests...")

        use_case = AnonymizeDatasetUseCase(
            self.logger,
            git_repository=self.git_repository
            or RepositoryFactory.create_repository(
                organisation="demo", project="git", name=f"project_{i}"
            ),
        )
        result = await use_case.execute(
            pull_requests,
            features,
            {"start_date": start_date, "end_date": end_date},
        )
        anonymized_pull_requests, anonymized_features = result

        anonymized_repository = use_case.get_anonymized_repository(git_repository)

        parameters_with_anonymized_repo = {
            "logger": self.logger,
            "git_repository": anonymized_repository,
        }
        json_repository_pull_request = PullRequestsJsonRepository(
            **parameters_with_anonymized_repo,
            path=f"{self.path}/pull_requests.json",
        )
        json_repository_features = FeaturesJsonRepository(
            **parameters_with_anonymized_repo,
            path=f"{self.path}/features.json",
        )

        self.logger.info(
            f"Saving {len(pull_requests)} pull requests to {json_repository_pull_request.path}"
        )
        await json_repository_pull_request.upsert_all(anonymized_pull_requests)

        self.logger.info(
            f"Saving {len(anonymized_features)} features to {json_repository_features.path}"
        )
        await json_repository_features.upsert_all(anonymized_features)

        return Branch(
            name=branch.name,
            repository=anonymized_repository,
        )

    @monitor("anonymizing database")
    async def execute(self, start_date=None, end_date=None):
        branches = settings.get_branches()

        anonymized_branches = await self.anonymize_branch.run_all(
            self,
            [
                (branch, start_date, end_date, index)
                for index, branch in enumerate(branches)
            ],
        )

        # create .env file for dataset
        replace_env_var(
            self.env_file_model,
            os.path.join(self.path, ".env"),
            "GIT_BRANCHES",
            json.dumps(
                [
                    anonymized_branch.to_dict()
                    for anonymized_branch in anonymized_branches
                ]
            ),
        )
