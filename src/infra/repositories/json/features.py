from src.domain.entities.feature import Feature
from src.domain.repositories.features import FeaturesRepository
from src.domain.repositories.utils import (
    raise_exception_if_repository_differs_from_entity,
)
from src.infra.repositories.json.base import BaseRepoJsonRepositoryMixin


class FeaturesJsonRepository(BaseRepoJsonRepositoryMixin[Feature], FeaturesRepository):
    entity_class = Feature  # type: ignore

    def __init__(self, logger, git_repository, path, *args, **kwargs):
        self.init(path, git_repository)
        super().__init__(logger=logger, git_repository=git_repository)

    async def upsert_all(self, entities, options=None) -> None:
        if not entities:
            return

        raise_exception_if_repository_differs_from_entity(
            self.git_repository, entities[0]
        )

        await super().upsert_all(entities, options)
