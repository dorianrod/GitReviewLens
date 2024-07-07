from typing import Optional, TypedDict

from src.common.monitoring.logger import LoggerInterface
from src.common.repositories.base_repository import BaseRepository
from src.domain.entities.pull_request import PullRequest
from src.domain.entities.repository import Repository
from src.domain.repositories.utils import (
    raise_exception_if_repository_differs_from_entity,
)


class PullRequestsFilters(TypedDict):
    start_date: Optional[str]
    end_date: Optional[str]
    exclude_ids: Optional[list[str]]


class PullRequestsRepository(BaseRepository[PullRequest, PullRequestsFilters, dict]):
    logger: LoggerInterface
    git_repository: Repository

    def __init__(
        self, logger: LoggerInterface, git_repository: str | dict | Repository
    ):
        self.logger = logger
        self.git_repository = Repository.parse(git_repository)

    async def upsert(self, entity, options=None):
        raise_exception_if_repository_differs_from_entity(self.git_repository, entity)
