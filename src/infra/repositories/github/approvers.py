import requests

from src.domain.entities.developer import Developer
from src.domain.entities.repository import Repository
from src.domain.repositories.developers import DeveloperRepository
from src.infra.repositories.github.utils import get_base_url, get_email, get_header


class ApproversGithubRepository(DeveloperRepository):
    max_results: int
    use_pagination: bool = True
    git_repository: Repository

    def __init__(self, git_repository: str | dict | Repository, *args, **kwargs):
        self.max_results = kwargs.pop("max_results") if "max_results" in kwargs else 100
        self.git_repository = Repository.parse(git_repository)
        super().__init__(*args, **kwargs)

    async def _get_all_approvers(self, pull_request_id, page=1):
        url = f"{get_base_url(self.git_repository)}/pulls/{pull_request_id}/reviews?per_page={self.max_results}&page={page}"

        response = requests.get(url, headers=get_header(self.git_repository))
        if response.status_code != 200:
            raise Exception(
                f"Unable to get approvers in Github: {str(response.content)}"
            )

        approvers_from_github = response.json()

        all_approvers = [
            review for review in approvers_from_github if review["state"] == "APPROVED"
        ]
        if self.use_pagination and len(approvers_from_github) == self.max_results:
            all_approvers += await self._get_all_approvers(
                page=page + 1, pull_request_id=pull_request_id
            )

        return all_approvers

    async def find_all(self, filters=None):
        pull_request = filters.get("pull_request")
        if not pull_request:
            raise Exception("No pull request provided")

        approvers_from_github = await self._get_all_approvers(
            pull_request_id=pull_request.source_id
        )

        approvers = []
        for approver in approvers_from_github:
            name = approver["user"]["login"]

            approvers.append(
                Developer.from_dict(
                    {
                        "full_name": name,
                        "email": get_email(name),
                    }
                )
            )

        return approvers
