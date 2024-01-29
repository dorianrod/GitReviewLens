from src.domain.entities.repository import Repository
from src.domain.entities.types import RepositoryTypes
from src.infra.repositories.azure.comments import CommentsAzureRepository
from src.infra.repositories.azure.pull_requests import PullRequestsAzureRepository
from src.infra.repositories.github.comments import CommentsGithubRepository
from src.infra.repositories.github.pull_requests import PullRequestsGithubRepository


def get_repositories_for_git_repository(
    git_repository: Repository,
):
    type = git_repository.type
    if type == RepositoryTypes.GITHUB:
        RemoteCommentRepository = CommentsGithubRepository  # type: ignore
        RemotePullRequestRepository = PullRequestsGithubRepository  # type: ignore
    elif type == RepositoryTypes.AZURE:
        RemoteCommentRepository = CommentsAzureRepository  # type: ignore
        RemotePullRequestRepository = PullRequestsAzureRepository  # type: ignore

    return {
        "comments": RemoteCommentRepository,
        "pull_requests": RemotePullRequestRepository,
    }
