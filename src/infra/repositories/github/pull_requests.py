import requests

from src.common.utils.date import parse_date
from src.domain.entities.pull_request import PullRequest
from src.domain.repositories.pull_requests import PullRequestsRepository
from src.infra.repositories.github.approvers import ApproversGithubRepository
from src.infra.repositories.github.utils import get_base_url, get_email, get_header


class PullRequestsGithubRepository(PullRequestsRepository):
    max_results: int
    use_pagination: bool = True

    def __init__(self, *args, **kwargs):
        self.max_results = kwargs.pop("max_results") if "max_results" in kwargs else 100
        super().__init__(*args, **kwargs)

    async def _get_all_pull_requests(self, start_date, end_date, page=1):
        MAX_RESULTS = self.max_results

        results = []

        url = f"{get_base_url(self.git_repository)}/pulls?state=closed&per_page={self.max_results}&page={page}"

        self.logger.info(f"Fetching pull requests from Github: {url}")

        response = requests.get(url, headers=get_header(self.git_repository))
        if response.status_code != 200:
            raise Exception(
                f"Unable to get pull requests in Github: {str(response.content)}"
            )

        pull_requests_from_github = response.json()
        results += pull_requests_from_github

        if self.use_pagination and len(pull_requests_from_github) == MAX_RESULTS:
            last_value = pull_requests_from_github[-1]
            last_date = parse_date(last_value["created_at"])
            if (not end_date or last_date <= end_date) and (
                not start_date or last_date >= start_date
            ):
                results += await self._get_all_pull_requests(
                    start_date, end_date, page + 1
                )

        return results

    async def find_all(self, filters=None):
        filters = filters or {}
        start_date = parse_date(filters.get("start_date"))
        end_date = parse_date(filters.get("end_date"))
        exclude_ids = set([str(id) for id in filters.get("exclude_ids", [])])

        self.logger.info(
            f"Fetching pull requests for {self.git_repository} Github from {start_date} to {end_date}"
        )

        approvers_repository = ApproversGithubRepository(
            git_repository=self.git_repository, logger=self.logger
        )

        pull_requests_from_github = await self._get_all_pull_requests(
            start_date, end_date
        )

        pull_requests: list[PullRequest] = []
        for pr in pull_requests_from_github:
            creation_date = parse_date(pr["created_at"])
            if not (
                (start_date is None or creation_date >= start_date)
                and (end_date is None or creation_date <= end_date)
            ):
                continue

            completion_date = pr["merged_at"]
            is_merged = pr["state"] == "closed" and completion_date is not None
            if is_merged:
                id = str(pr["number"])

                if id in exclude_ids:
                    continue
                created_by_name = pr["user"]["login"]
                created_by_email = get_email(created_by_name)

                pull_request = PullRequest.from_dict(
                    {
                        "creation_date": creation_date,
                        "completion_date": completion_date,
                        "created_by": {
                            "full_name": created_by_name,
                            "email": created_by_email,
                        },
                        "source_id": id,
                        "git_repository": self.git_repository,
                        "approvers": [],
                        "comments": [],
                        "title": pr["title"],
                        "source_branch": pr["head"]["ref"],
                        "target_branch": pr["base"]["ref"],
                        "commit": pr["merge_commit_sha"],
                        "previous_commit": pr["base"]["sha"],
                    }
                )

                approvers = await approvers_repository.find_all(
                    {"pull_request": pull_request}
                )
                pull_request.approvers = approvers

                pull_requests.append(pull_request)

        return pull_requests
