import requests

from src.common.utils.date import is_in_range, parse_date
from src.domain.entities.pull_request import PullRequest
from src.domain.repositories.pull_requests import PullRequestsRepository
from src.infra.repositories.azure.constants import APPROVE, APPROVE_WITH_SUGGESTION
from src.infra.repositories.azure.utils import get_base_url, get_header


class PullRequestsAzureRepository(PullRequestsRepository):
    max_results: int
    use_pagination: bool = True

    def __init__(self, *args, **kwargs):
        self.max_results = (
            kwargs.pop("max_results") if "max_results" in kwargs else 1000
        )
        super().__init__(*args, **kwargs)

    async def _get_all_pull_requests(self, start_date, end_date, skip=0):
        MAX_RESULTS = self.max_results

        results = []

        url = f"{get_base_url(self.git_repository)}/pullRequests?searchCriteria.status=all&$top={MAX_RESULTS}&$skip={skip}"
        self.logger.info(f"Fetching pull requests from Azure: {url}")

        response = requests.get(url, headers=get_header(self.git_repository))
        if response.status_code != 200:
            raise Exception(
                f"Unable to get pull requests in Azure: {str(response.content)}"
            )

        data = response.json()
        results = data["value"]
        if self.use_pagination and len(data["value"]) == MAX_RESULTS:
            last_value = data["value"][-1]
            last_date = parse_date(last_value.get("creationDate"))
            if is_in_range(last_date, start_date, end_date):
                results += await self._get_all_pull_requests(
                    start_date, end_date, skip + MAX_RESULTS
                )

        return results

    async def find_all(self, filters=None):
        filters = filters or {}

        start_date = parse_date(filters.get("start_date"))
        end_date = parse_date(filters.get("end_date"))
        exclude_ids = set([str(id) for id in filters.get("exclude_ids", [])])

        self.logger.info(
            f"Fetching pull requests in {self.git_repository} Azure from {start_date} to {end_date}"
        )

        pull_requests_from_azure = await self._get_all_pull_requests(
            start_date, end_date
        )

        pull_requests: list[PullRequest] = []
        for pr in pull_requests_from_azure:
            creation_date = parse_date(pr.get("creationDate"))
            if not is_in_range(creation_date, start_date, end_date):
                continue

            id = str(pr["pullRequestId"])
            if id in exclude_ids:
                continue

            is_merged = pr["status"] == "completed"
            if is_merged:
                completion_date = pr.get("closedDate")
                created_by_name = pr["createdBy"]["displayName"]
                created_by_email = pr["createdBy"]["uniqueName"]
                reviewers = pr["reviewers"]

                approvers = []
                for reviewer in reviewers:
                    if (
                        reviewer["vote"] == APPROVE
                        or reviewer["vote"] == APPROVE_WITH_SUGGESTION
                    ):
                        reviewer_name = reviewer["displayName"]
                        reviewer_email = reviewer["uniqueName"]
                        approvers.append(
                            {
                                "full_name": reviewer_name,
                                "email": reviewer_email,
                            }
                        )

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
                        "approvers": approvers,
                        "comments": [],
                        "title": pr["title"],
                        "source_branch": pr["sourceRefName"],
                        "target_branch": pr["targetRefName"],
                        "commit": pr["lastMergeTargetCommit"]["commitId"],
                        "previous_commit": pr["lastMergeSourceCommit"]["commitId"],
                    }
                )
                pull_requests.append(pull_request)

        return pull_requests
