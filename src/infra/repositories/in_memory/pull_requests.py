from collections import defaultdict

from src.common.monitoring.logger import LoggerInterface
from src.domain.entities.comment import Comment
from src.domain.entities.pull_request import PullRequest
from src.domain.entities.repository import Repository
from src.domain.repositories.pull_requests import PullRequestsRepository
from src.domain.repositories.utils import (
    raise_exception_if_repository_differs_from_entity,
)
from src.infra.repositories.in_memory.base import BaseInMemoryRepositoryMixin
from src.infra.repositories.in_memory.comments import CommentsInMemoryRepository


class PullRequestsInMemoryRepository(
    BaseInMemoryRepositoryMixin[PullRequest], PullRequestsRepository
):
    def __init__(self, logger: LoggerInterface, git_repository: Repository | str):
        self.comments_repository = CommentsInMemoryRepository(
            logger=logger, git_repository=git_repository
        )
        super().__init__(logger, git_repository)

    async def upsert(self, entity, options=None):
        raise_exception_if_repository_differs_from_entity(self.git_repository, entity)

        await super().upsert(entity, options)

        await self.comments_repository.upsert_all(
            [
                Comment.from_dict({**comment.to_dict(), "pull_request_id": entity.id})
                for comment in entity.comments
            ]
        )

    async def find_all(self, filters=None):
        filters = filters or {}
        exclude_ids = filters.get("exclude_ids", [])

        pull_requests = [
            pull_request
            for pull_request in self.entities_by_ids.values()
            if pull_request.id not in exclude_ids
            and self.git_repository == pull_request.git_repository
        ]

        comments_by_pull_requests = defaultdict(list)

        if pull_requests:
            comments = await self.comments_repository.find_all(
                {"pull_requests": pull_requests}
            )
            for comment in comments:
                comments_by_pull_requests[comment.pull_request_id].append(comment)

            for pull_request in pull_requests:
                pull_request.comments = comments_by_pull_requests[pull_request.id]

        return pull_requests
