import itertools

from src.common.utils.worker import concurrency_aio
from src.domain.entities.comment import Comment
from src.domain.repositories.comments import CommentsRepository
from src.infra.paginator_fetcher import PaginatorWorker
from src.infra.repositories.github.utils import (
    get_base_url,
    get_email,
    get_header,
    non_blocking_error_codes,
)


class CommentsGithubRepository(CommentsRepository):
    def __init__(self, pagination={}, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pagination = {
            "max_concurrency": 3,
            "items_per_page": 100,
            **pagination,
        }

    @concurrency_aio(max_concurrency=50)
    async def __get_comments_for_pull_request(self, pull_request, exclude_ids):
        worker = CommentPaginatorWorker(
            pull_request=pull_request,
            git_repository=self.git_repository,
            headers=get_header(self.git_repository),
            logger=self.logger,
            non_blocking_error_codes=non_blocking_error_codes,
            **self.pagination,
        )

        comments: list[dict] = []
        iterator = await worker.fetch(exclude_ids)
        async for row in iterator:
            comments = comments + row

        return comments

    async def find_all(self, filters=None):
        filters = filters or {}
        authors_to_exclude = filters.get("authors_to_exclude", [])

        pull_requests = filters.get("pull_requests", [])
        if not pull_requests:
            return []

        exclude_ids = set([str(id) for id in filters.get("exclude_ids", [])])

        self.logger.info(
            f"Fetching comments in {self.git_repository} Github for {len(pull_requests)} pull requests"
        )

        rows = await self.__get_comments_for_pull_request.run_all(
            self, [(pull_request, exclude_ids) for pull_request in pull_requests]
        )
        comments = []

        for row in itertools.chain.from_iterable(rows):
            author = row["developer"]["full_name"]
            if author in authors_to_exclude:
                continue
            comments.append(Comment.from_dict(row))

        return comments


class CommentPaginatorWorker(PaginatorWorker):
    def __init__(self, *args, **kwargs):
        self.git_repository = kwargs.pop("git_repository")
        self.pull_request = kwargs.pop("pull_request")
        super().__init__(*args, **kwargs)

    async def get_url(self, page: int) -> str:
        return f"{get_base_url(self.git_repository)}/pulls/{self.pull_request.source_id}/comments?per_page={self.items_per_page}&page={page + 1}"

    async def process_data(self, data, options=None):
        rows = data
        if len(rows) == 0:
            return [], False

        transformed_rows = []

        for row in rows:
            author = row["user"]["login"]
            email = get_email(author)

            transformed_rows.append(
                {
                    "pull_request_id": self.pull_request.id,
                    "creation_date": row["created_at"],
                    "content": row["body"],
                    "developer": {
                        "full_name": author,
                        "email": email,
                    },
                }
            )

        return transformed_rows, len(rows) == self.items_per_page
