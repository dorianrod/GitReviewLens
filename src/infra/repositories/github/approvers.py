from src.common.utils.worker import concurrency_aio
from src.domain.entities.developer import Developer
from src.domain.entities.repository import Repository
from src.domain.repositories.developers import DeveloperRepository
from src.infra.paginator_fetcher import PaginatorWorker
from src.infra.repositories.github.utils import (
    get_base_url,
    get_email,
    get_header,
    non_blocking_error_codes,
)


class ApproversGithubRepository(DeveloperRepository):
    def __init__(
        self, git_repository: str | dict | Repository, pagination={}, *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.pagination = {
            "max_concurrency": 3,
            "items_per_page": 100,
            **pagination,
        }
        self.git_repository = Repository.parse(git_repository)

    @concurrency_aio(max_concurrency=50)
    async def __get_reviewers_for_pull_request(self, pull_request):
        worker = ApproverPaginatorWorker(
            pull_request=pull_request,
            git_repository=self.git_repository,
            headers=get_header(self.git_repository),
            logger=self.logger,
            non_blocking_error_codes=non_blocking_error_codes,
            **self.pagination,
        )

        approvers: list[dict] = []
        iterator = await worker.fetch()
        async for row in iterator:
            approvers = approvers + row

        return (approvers, pull_request)

    async def find_all(self, filters=None):
        filters = filters or {}

        pull_requests = filters.get("pull_requests", [])
        if not pull_requests:
            return []

        self.logger.info(
            f"Fetching approvers in {self.git_repository} Github for {len(pull_requests)} pull requests"
        )

        rows = await self.__get_reviewers_for_pull_request.run_all(self, pull_requests)

        approvers = []
        for approvers_for_pull_request, pull_request in rows:
            approvers.append(
                (
                    [
                        Developer.from_dict(approver)
                        for approver in approvers_for_pull_request
                    ],
                    pull_request,
                )
            )

        return approvers


class ApproverPaginatorWorker(PaginatorWorker):
    def __init__(self, *args, **kwargs):
        self.git_repository = kwargs.pop("git_repository")
        self.pull_request = kwargs.pop("pull_request")
        super().__init__(*args, **kwargs)

    async def get_url(self, page: int) -> str:
        return f"{get_base_url(self.git_repository)}/pulls/{self.pull_request.source_id}/reviews?per_page={self.items_per_page}&page={page + 1}"

    async def process_data(self, data, options=None):
        rows = data
        if len(rows) == 0:
            return [], False

        transformed_rows = []

        for row in rows:
            if row["state"] == "APPROVED":
                author = row["user"]["login"]
                email = get_email(author)

                transformed_rows.append(
                    {
                        "full_name": author,
                        "email": email,
                    }
                )

        return transformed_rows, len(rows) == self.items_per_page
