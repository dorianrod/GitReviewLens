from collections import defaultdict

from src.common.monitoring.logger import LoggerInterface
from src.domain.entities.pull_request import PullRequest
from src.domain.entities.repository import Repository
from src.domain.exceptions import NotExistsException
from src.domain.repositories.pull_requests import PullRequestsRepository
from src.infra.repositories.in_memory.comments import CommentsInMemoryRepository


class PullRequestsInMemoryRepository(PullRequestsRepository):
    pull_requests: dict[str, PullRequest]
    pull_requests_by_source_id: dict[str, PullRequest]

    def __init__(self, logger: LoggerInterface, git_repository: Repository | str):
        self.pull_requests = {}
        self.pull_requests_by_source_id = {}
        self.comments_repository = CommentsInMemoryRepository(
            logger=logger, git_repository=git_repository
        )
        super().__init__(logger, git_repository)

    async def get_by_id(self, id):
        entity = self.pull_requests.get(id)
        if entity:
            return entity

        raise NotExistsException(f"Pull request {id} not found")

    async def upsert(self, entity, options=None):
        await super().upsert(entity, options)
        self.pull_requests[entity.id] = entity
        self.pull_requests_by_source_id[entity.source_id] = entity
        await self.comments_repository.upsert_all(
            entity.comments, {"pull_request": entity}
        )

    async def find_all(self, filters=None):
        filters = filters or {}
        exclude_ids = filters.get("exclude_ids", [])

        pull_requests = [
            pull_request
            for pull_request in self.pull_requests.values()
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
