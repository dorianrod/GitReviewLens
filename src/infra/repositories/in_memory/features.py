from src.common.monitoring.logger import LoggerInterface
from src.domain.entities.feature import Feature
from src.domain.entities.repository import Repository
from src.domain.repositories.features import FeaturesRepository


class FeaturesInMemoryRepository(FeaturesRepository):
    features: dict[str, Feature]

    def __init__(self, logger: LoggerInterface, git_repository: Repository | str):
        self.features = {}
        super().__init__(logger, git_repository)

    async def get_by_id(self, id):
        return self.features[id]

    async def upsert(self, entity, options=None):
        await super().upsert(entity, options)
        self.features[entity.id] = entity

    async def find_all(self, filters=None):
        filters = filters or {}
        exclude_ids = filters.get("exclude_ids", [])

        return [
            feature
            for feature in self.features.values()
            if feature.id not in exclude_ids
            and self.git_repository == feature.git_repository
        ]
