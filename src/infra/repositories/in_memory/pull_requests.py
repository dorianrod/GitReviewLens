from src.common.monitoring.logger import LoggerInterface
from src.domain.entities.pull_request import PullRequest
from src.domain.entities.repository import Repository
from src.domain.exceptions import NotExistsException
from src.domain.repositories.pull_requests import PullRequestsRepository


class PullRequestsInMemoryRepository(PullRequestsRepository):
    pull_requests: dict[str, PullRequest]
    pull_requests_by_source_id: dict[str, PullRequest]

    def __init__(self, logger: LoggerInterface, git_repository: Repository | str):
        self.pull_requests = {}
        self.pull_requests_by_source_id = {}
        super().__init__(logger, git_repository)

    def get_by_id(self, id):
        entity = self.pull_requests.get(id)
        if entity:
            return entity

        raise NotExistsException(f"Pull request {id} not found")

    def upsert(self, entity, options=None):
        super().upsert(entity, options)
        self.pull_requests[entity.id] = entity
        self.pull_requests_by_source_id[entity.source_id] = entity

    def find_all(self, filters=None):
        filters = filters or {}
        exclude_ids = filters.get("exclude_ids", [])

        return [
            pull_request
            for pull_request in self.pull_requests.values()
            if pull_request.id not in exclude_ids
            and self.git_repository == pull_request.git_repository
        ]
