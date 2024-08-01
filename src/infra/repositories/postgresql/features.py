from sqlalchemy import select
from sqlalchemy.orm import joinedload

from src.domain.repositories.features import FeaturesRepository
from src.domain.repositories.utils import (
    raise_exception_if_repository_differs_from_entity,
)
from src.infra.database.postgresql.models.models import Feature as FeatureModel
from src.infra.repositories.postgresql.generic_db import GenericDatabaseRepository
from src.infra.repositories.postgresql.upsert_all_developers import (
    UpsertAllDevelopersMixin,
)


class FeaturesDatabaseRepository(
    FeaturesRepository, GenericDatabaseRepository, UpsertAllDevelopersMixin
):
    Model = FeatureModel

    async def upsert_all(self, entities, options=None) -> None:
        if not entities:
            return

        try:
            related_objects_options = options or {}
            related_objects_options.pop("is_new")
        except KeyError:
            pass

        raise_exception_if_repository_differs_from_entity(
            self.git_repository, entities[0]
        )

        await self.upsert_all_developers(entities, related_objects_options)
        await self._upsert_all_entities_within_transaction(entities, options)

    async def _select_find_all(self, session, options=None):
        Model = self.Model

        query = (
            select(Model)
            .options(joinedload(Model.developer))
            .filter(Model.repository == self.git_repository.path)
        )
        return query
