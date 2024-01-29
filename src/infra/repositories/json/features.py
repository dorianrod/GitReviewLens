from src.domain.entities.feature import Feature
from src.domain.repositories.features import FeaturesRepository
from src.infra.repositories.json.base import BaseRepoJsonRepositoryMixin


class FeaturesJsonRepository(BaseRepoJsonRepositoryMixin[Feature], FeaturesRepository):
    entity_class = Feature  # type: ignore

    def __init__(self, logger, git_repository, path, *args, **kwargs):
        self.init(path, git_repository)
        super().__init__(logger=logger, git_repository=git_repository)
