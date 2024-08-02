from collections import defaultdict

from src.common.utils.date import parse_date
from src.domain.entities.pull_request import PullRequest
from src.domain.repositories.pull_requests import PullRequestsRepository
from src.infra.paginator_fetcher import PaginatorWorker
from src.infra.repositories.github.approvers import ApproversGithubRepository
from src.infra.repositories.github.comments import CommentsGithubRepository
from src.infra.repositories.github.utils import get_base_url, get_email, get_header


class PullRequestsGithubRepository(PullRequestsRepository):
    def __init__(self, pagination={}, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pagination = {
            "max_concurrency": 20,
            "items_per_page": 100,
            **pagination,
        }

    async def __get_pull_requests_from_github(self, start_date, end_date):
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

        pull_requests_from_azure = await self.__get_pull_requests_from_github(
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

        if pull_requests:
            # Gettings approvers
            approvers_repo = ApproversGithubRepository(
                logger=self.logger, git_repository=self.git_repository
            )
            approvers_and_pull_request = await approvers_repo.find_all(
                {"pull_requests": pull_requests}
            )
            approvers_by_pull_request_id = defaultdict(list)
            for approvers, pull_request in approvers_and_pull_request:
                approvers_by_pull_request_id[pull_request.id] = approvers

            # Getting comments
            comments_by_pull_request_id = defaultdict(list)
            comments_repo = CommentsGithubRepository(
                logger=self.logger, git_repository=self.git_repository
            )
            comments = await comments_repo.find_all({"pull_requests": pull_requests})
            for comment in comments:
                comments_by_pull_request_id[comment.pull_request_id].append(comment)

            # Complete data
            for pull_request in pull_requests:
                pull_request.comments = comments_by_pull_request_id[pull_request.id]
                pull_request.approvers = approvers_by_pull_request_id[pull_request.id]

        return pull_requests


class PullRequestPaginatorWorker(PaginatorWorker):
    def __init__(self, *args, **kwargs):
        self.git_repository = kwargs.pop("git_repository")
        self.start_date = kwargs.pop("start_date")
        self.end_date = kwargs.pop("end_date")
        super().__init__(*args, **kwargs)

    async def get_url(self, page: int) -> str:
        return f"{get_base_url(self.git_repository)}/pulls?state=closed&per_page={self.items_per_page}&page={page + 1}"

    async def process_data(self, data, options=None):
        rows = data
        if len(rows) == 0:
            return [], False

        transformed_rows = []

        for row in rows:
            creation_date = parse_date(row["created_at"])
            if not (
                (self.start_date is None or creation_date >= self.start_date)
                and (self.end_date is None or creation_date <= self.end_date)
            ):
                continue

            completion_date = row["merged_at"]
            is_merged = row["state"] == "closed" and completion_date is not None
            id = str(row["number"])

            created_by_name = row["user"]["login"]
            created_by_email = get_email(created_by_name)

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
                    "git_repository": self.git_repository,
                    "approvers": [],
                    "comments": [],
                    "title": row["title"],
                    "source_branch": row["head"]["ref"],
                    "target_branch": row["base"]["ref"],
                    "commit": row["merge_commit_sha"],
                    "previous_commit": row["base"]["sha"],
                }
            )

        return transformed_rows, len(transformed_rows) == self.items_per_page
