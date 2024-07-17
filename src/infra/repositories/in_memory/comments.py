import itertools
from collections import defaultdict
from typing import Optional

from src.common.monitoring.logger import LoggerInterface
from src.domain.entities.comment import Comment
from src.domain.entities.pull_request import PullRequest
from src.domain.entities.repository import Repository
from src.domain.repositories.comments import CommentsRepository


class CommentsInMemoryRepository(CommentsRepository):
    comments_by_pr: dict[str, list[Comment]]

    def __init__(self, logger: LoggerInterface, git_repository: str | Repository):
        super().__init__(logger, git_repository)
        self.comments_by_pr = defaultdict(list)

    async def upsert(self, entity, options=None):
        await super().upsert(entity, options)

        options = options or {}
        pull_request: Optional[PullRequest] = options.get("pull_request")

        if not pull_request:
            raise Exception("Pull request not provided for comment")

        entity.pull_request_id = pull_request.id

        self.comments_by_pr[pull_request.source_id].append(entity)

    async def find_all(self, filters=None):
        pull_requests_ids = self._get_pull_requests_from_options(filters)

        comments: list[list[Comment]] = [
            self.comments_by_pr.get(source_id, [])
            for (source_id, _id) in pull_requests_ids
        ]

        return list(itertools.chain.from_iterable(comments))
