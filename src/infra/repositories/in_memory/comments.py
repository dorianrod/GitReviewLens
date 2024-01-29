from src.common.monitoring.logger import LoggerInterface
from src.domain.entities.comment import Comment
from src.domain.entities.pull_request import PullRequest
from src.domain.entities.repository import Repository
from src.domain.repositories.comments import CommentsRepository


class CommentsInMemoryRepository(CommentsRepository):
    comments_by_pr: dict[str, Comment]

    def __init__(self, logger: LoggerInterface, git_repository: str | Repository):
        super().__init__(logger, git_repository)
        self.comments_by_pr = {}

    def upsert(self, entity, options=None):
        super().upsert(entity, options)

        options = options or {}
        pull_request: PullRequest = options.get("pull_request")

        self.comments_by_pr[pull_request.id] = entity

    def find_all(self, filters=None):
        filters = filters or {}

        pull_request = filters.get("pull_request")
        if not pull_request:
            raise NotImplementedError()

        comment = self.comments_by_pr.get(pull_request.id)
        return [comment] if comment else []
