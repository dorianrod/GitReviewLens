from sqlalchemy import select
from sqlalchemy.orm import joinedload

from src.domain.repositories.features import FeaturesRepository
from src.infra.database.postgresql.models.models import Feature as FeatureModel
from src.infra.repositories.postgresql.developers import DeveloperDatabaseRepository
from src.infra.repositories.postgresql.generic_db import GenericDatabaseRepository


class FeaturesDatabaseRepository(GenericDatabaseRepository, FeaturesRepository):
    Model = FeatureModel

    async def upsert(self, entity, options=None):
        options = options or {}

        upsert_developer = options.get("upsert_developer", True)
        if upsert_developer:
            developer_repository = DeveloperDatabaseRepository(logger=self.logger)
            await developer_repository.upsert(entity.developer)

        await super().upsert(entity, options)

    async def _select_find_all(self, session, options=None):
        query = (
            select(FeatureModel)
            .options(joinedload(FeatureModel.developer))
            .filter(FeatureModel.repository == self.git_repository.path)
        )
        return query
