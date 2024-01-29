from dataclasses import dataclass
from datetime import datetime
from typing import Sequence

from src.app.controllers.base_controller import BaseController
from src.app.utils.monitor import monitor
from src.common.monitoring.logger import LoggerInterface
from src.domain.entities.feature import Feature
from src.infra.repositories.git.features import FeaturesGit
from src.infra.repositories.git.repositories import GitRepoLocal
from src.infra.repositories.postgresql.features import FeaturesDatabaseRepository
from src.settings import settings


@dataclass
class LoadFeaturesController(BaseController[None, Sequence[Feature]]):
    logger: LoggerInterface
    path: str = "/repos"

    @monitor("Loading features from repositories")
    def execute(self, options=None) -> Sequence[Feature]:
        if not options:
            options = {}

        branches = settings.get_branches()

        for branch in branches:
            repository = branch.repository

            db_features_repository = FeaturesDatabaseRepository(
                logger=self.logger, git_repository=repository
            )
            features_in_db = db_features_repository.find_all()

            self.logger.info(f"Loading features from repository {repository.name}...")
            max_date = None
            for feature in features_in_db:
                if max_date is None or feature.date > max_date:
                    max_date = feature.date

            repo_path = f"{self.path}/{repository.name}"
            GitRepoLocal(logger=self.logger).checkout(
                branch=branch,
            )
            features_repository = FeaturesGit(logger=self.logger, path=repo_path)
            features_from_git = features_repository.find_all(
                {
                    "from_date": max_date,
                    "to_date": datetime.now().isoformat(),
                    "branch": branch.name,
                    "git_repository": repository,
                    **options,
                }
            )
            db_features_repository.upsert_all(features_from_git)
            self.logger.info(
                f"{len(features_from_git)} features from repository {repository.name} loaded..."
            )
        return features_from_git
