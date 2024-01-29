from faker import Faker

from src.common.utils.string import clean_string
from src.domain.entities.pull_request import PullRequest
from src.domain.factories.developer import DeveloperFactory
from src.domain.factories.repository import RepositoryFactory
from src.domain.factories.util import get_random_title


class PullRequestFactory:
    @staticmethod
    def create_pull_request(
        title=None,
        source_branch=None,
        target_branch=None,
        created_by=None,
        git_repository=None,
        **kwargs,
    ):
        fake = Faker()
        title = title or get_random_title()
        target_branch = target_branch or "origin/master"
        source_branch = source_branch or (
            "origin/refs/heads/" + clean_string(fake.word())
        )
        created_by = created_by or DeveloperFactory.create_developer()
        git_repository = git_repository or RepositoryFactory.create_repository()
        return PullRequest.from_dict(
            {
                "created_by": created_by,
                "git_repository": git_repository,
                "title": title,
                "target_branch": target_branch,
                "source_branch": source_branch,
                **kwargs,
            }
        )
