from typing import TypedDict

from src.common.monitoring.logger import LoggerInterface
from src.common.repositories.base_repository import BaseRepository
from src.domain.entities.comment import Comment
from src.domain.entities.pull_request import PullRequest
from src.domain.entities.repository import Repository
from src.domain.repositories.utils import (
    raise_exception_if_repository_differs_from_entity,
)


class CommentUpsertOptions(TypedDict):
    pull_request: PullRequest


class CommentsRepository(BaseRepository[Comment, dict, CommentUpsertOptions]):
    logger: LoggerInterface
    git_repository: Repository

    def __init__(
        self, logger: LoggerInterface, git_repository: str | dict | Repository
    ):
        self.logger = logger
        self.git_repository = Repository.parse(git_repository)

    async def upsert(self, entity, options=None):
        options = options or {}
        pull_request: PullRequest = options["pull_request"]

        raise_exception_if_repository_differs_from_entity(
            self.git_repository, pull_request
        )

    def _get_pull_requests_from_options(self, filters=None):
        filters = filters or {}
        pull_requests = filters.get("pull_requests")
        pull_request = filters.get("pull_request")
        pull_requests_ids: list[str] = [
            (pr.source_id, pr.id) for pr in ([pull_request] if pull_request else pull_requests or [])  # type: ignore
        ]

        if not pull_requests_ids:
            raise Exception("No pull request provided")

        return pull_requests_ids
