from src.domain.entities.feature import Feature
from src.domain.repositories.features import FeaturesRepository
from src.domain.repositories.utils import (
    raise_exception_if_repository_differs_from_entity,
)
from src.infra.repositories.in_memory.base import BaseInMemoryRepositoryMixin


class FeaturesInMemoryRepository(
    BaseInMemoryRepositoryMixin[Feature], FeaturesRepository
):
    async def find_all(self, filters=None):
        filters = filters or {}
        exclude_ids = filters.get("exclude_ids", [])

        return [
            feature
            for feature in self.entities_by_ids.values()
            if feature.id not in exclude_ids
            and self.git_repository == feature.git_repository
        ]

    async def upsert(self, entity: Feature, options=None):
        raise_exception_if_repository_differs_from_entity(self.git_repository, entity)

        await super().upsert(entity, options)
