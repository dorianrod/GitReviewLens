from src.common.utils.date import is_in_range, parse_date
from src.domain.entities.pull_request import PullRequest
from src.domain.repositories.pull_requests import PullRequestsRepository
from src.infra.paginator_fetcher import PaginatorWorker
from src.infra.repositories.azure.constants import APPROVE, APPROVE_WITH_SUGGESTION
from src.infra.repositories.azure.utils import get_base_url, get_header


class PullRequestsAzureRepository(PullRequestsRepository):
    def __init__(self, pagination={}, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pagination = {
            "max_concurrency": 3,
            "items_per_page": 1000,
            **pagination,
        }

    async def __get_pull_requests_from_azure(self, start_date, end_date):
        worker = PullRequestPaginatorWorker(
            start_date=start_date,
            end_date=end_date,
            git_repository=self.git_repository,
            headers=get_header(self.git_repository),
            logger=self.logger,
            **self.pagination,
        )

        pull_requests: list[dict] = []
        iterator = await worker.fetch()
        async for row in iterator:
            pull_requests = pull_requests + row

        return pull_requests

    async def find_all(self, filters=None):
        filters = filters or {}
        start_date = parse_date(filters.get("start_date"))
        end_date = parse_date(filters.get("end_date"))
        exclude_ids = set([str(id) for id in filters.get("exclude_ids", [])])

        self.logger.info(
            f"Fetching pull requests in {self.git_repository} Azure from {start_date} to {end_date}"
        )

        pull_requests_from_azure = await self.__get_pull_requests_from_azure(
            start_date, end_date
        )

        pull_requests: list[PullRequest] = []
        for pr in pull_requests_from_azure:
            source_id = str(pr["source_id"])
            if source_id in exclude_ids:
                continue

            is_merged = pr["is_merged"]
            if not is_merged:
                continue

            pull_request = PullRequest.from_dict(
                {"git_repository": self.git_repository, **pr}
            )
            pull_requests.append(pull_request)

        return pull_requests


class PullRequestPaginatorWorker(PaginatorWorker):
    def __init__(self, *args, **kwargs):
        self.git_repository = kwargs.pop("git_repository")
        self.start_date = kwargs.pop("start_date")
        self.end_date = kwargs.pop("end_date")
        super().__init__(*args, **kwargs)

    async def get_url(self, page: int) -> str:
        skip = page * self.items_per_page
        return f"{get_base_url(self.git_repository)}/pullRequests?searchCriteria.status=all&$top={self.items_per_page}&$skip={skip}"

    async def process_data(self, data):
        rows = data["value"]
        if len(rows) == 0:
            return [], False

        transformed_rows = []

        for row in rows:
            creation_date = row.get("creationDate")
            if not is_in_range(
                parse_date(creation_date), self.start_date, self.end_date
            ):
                continue

            id = str(row["pullRequestId"])
            is_merged = row["status"] == "completed"
            completion_date = row.get("closedDate")
            created_by_name = row["createdBy"]["displayName"]
            created_by_email = row["createdBy"]["uniqueName"]
            reviewers = row["reviewers"]

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

            commit = row.get("lastMergeTargetCommit", None)
            previous_commit = row.get("lastMergeSourceCommit", None)

            transformed_rows.append(
                {
                    "is_merged": is_merged,
                    "creation_date": creation_date,
                    "completion_date": completion_date,
                    "created_by": {
                        "full_name": created_by_name,
                        "email": created_by_email,
                    },
                    "source_id": id,
                    "approvers": approvers,
                    "comments": [],
                    "title": row["title"],
                    "source_branch": row["sourceRefName"],
                    "target_branch": row.get("targetRefName"),
                    "commit": commit["commitId"] if commit else None,
                    "previous_commit": (
                        previous_commit["commitId"] if previous_commit else None
                    ),
                }
            )

        return transformed_rows, len(transformed_rows) == self.items_per_page
