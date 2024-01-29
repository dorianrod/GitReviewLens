from src.common.monitoring.logger import LoggerInterface
from src.common.repositories.base_repository import BaseRepository
from src.domain.entities.feature import Feature
from src.domain.entities.repository import Repository
from src.domain.repositories.utils import (
    raise_exception_if_repository_differs_from_entity,
)


class FeaturesRepository(BaseRepository[Feature, dict, dict]):
    logger: LoggerInterface
    git_repository: Repository

    def __init__(self, logger: LoggerInterface, git_repository: str | Repository):
        self.logger = logger
        self.git_repository = Repository.parse(git_repository)

    def upsert(self, entity, options=None):
        raise_exception_if_repository_differs_from_entity(self.git_repository, entity)
