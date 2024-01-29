from src.domain.entities.pull_request import PullRequest
from src.domain.repositories.pull_requests import PullRequestsRepository
from src.infra.repositories.json.base import BaseRepoJsonRepositoryMixin


class PullRequestsJsonRepository(
    BaseRepoJsonRepositoryMixin[PullRequest], PullRequestsRepository
):
    entity_class = PullRequest  # type: ignore

    def __init__(self, logger, git_repository, path, *args, **kwargs):
        self.init(path, git_repository)
        super().__init__(logger=logger, git_repository=git_repository)
