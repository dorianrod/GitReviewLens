import itertools
from collections import defaultdict

from src.common.monitoring.logger import LoggerInterface
from src.domain.entities.comment import Comment
from src.domain.entities.repository import Repository
from src.domain.repositories.comments import CommentsRepository
from src.infra.repositories.in_memory.base import BaseInMemoryRepositoryMixin


class CommentsInMemoryRepository(
    BaseInMemoryRepositoryMixin[Comment], CommentsRepository
):
    comments_by_pr: dict[str, list[Comment]]

    def __init__(self, logger: LoggerInterface, git_repository: str | Repository):
        super().__init__(logger, git_repository)
        self.comments_by_pr = defaultdict(list)

    async def upsert(self, entity, options=None):
        await super().upsert(entity, options)

        if not entity.pull_request_id:
            raise Exception("No pull request id provided for comment")

        self.comments_by_pr[entity.pull_request_id].append(entity)

    async def find_all(self, filters=None):
        pull_requests_ids = self._get_pull_requests_from_options(filters)

        comments: list[list[Comment]] = [
            self.comments_by_pr.get(id, []) for (_source_id, id) in pull_requests_ids
        ]

        return list(itertools.chain.from_iterable(comments))
