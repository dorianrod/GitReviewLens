import itertools
from dataclasses import dataclass
from datetime import datetime
from typing import Sequence

from src.app.controllers.base_controller import BaseController
from src.app.utils.monitor import monitor
from src.common.monitoring.logger import LoggerInterface
from src.common.settings import settings
from src.common.utils.worker import concurrency_aio
from src.domain.entities.feature import Feature
from src.infra.repositories.git.features import FeaturesGit
from src.infra.repositories.git.repositories import GitRepoLocal
from src.infra.repositories.postgresql.features import FeaturesDatabaseRepository


@dataclass
class LoadFeaturesController(BaseController[None, Sequence[Feature]]):
    logger: LoggerInterface
    path: str = "/repos"

    @concurrency_aio(max_concurrency=5)
    async def load_from_repository(self, branch, options):
        repository = branch.repository

        self.logger.info(f"Loading features from repository {repository.name}...")
        max_date = options.get("from_date", None)

        db_features_repository = FeaturesDatabaseRepository(
            logger=self.logger, git_repository=repository
        )
        if not max_date:
            features_in_db = await db_features_repository.find_all()
            # TODO Not optimized, implements optimized operations within repositories
            for feature in features_in_db:
                if max_date is None or feature.date > max_date:
                    max_date = feature.date

        repo_path = f"{self.path}/{repository.name}"
        GitRepoLocal(logger=self.logger).checkout(
            branch=branch,
        )
        features_repository = FeaturesGit(logger=self.logger, path=repo_path)
        features_from_git = await features_repository.find_all(
            {
                "from_date": max_date,
                "to_date": datetime.now().isoformat(),
                "branch": branch.name,
                "git_repository": repository,
                **options,
            }
        )
        await db_features_repository.upsert_all(features_from_git)
        self.logger.info(
            f"{len(features_from_git)} features from repository {repository.name} loaded..."
        )
        return features_from_git

    @monitor("Loading features from repositories")
    async def execute(self, options=None) -> Sequence[Feature]:
        if not options:
            options = {}

        branches = settings.get_branches()

        features = await self.load_from_repository.run_all(
            self, [(branch, options) for branch in branches]
        )
        return list(itertools.chain.from_iterable(features))
