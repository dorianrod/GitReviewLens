import itertools

import aiohttp

from src.app.utils.monitor import monitor
from src.common.utils.worker import concurrency_aio
from src.domain.entities.comment import Comment
from src.domain.entities.pull_request import PullRequest
from src.domain.repositories.comments import CommentsRepository
from src.infra.repositories.azure.utils import get_base_url, get_header
from src.infra.requests.fetch import async_fetch


class CommentsAzureRepository(CommentsRepository):
    @concurrency_aio(max_concurrency=50)
    async def __fetch_comments_for_pull_requests(self, pull_request_source_id, options):
        filters = options or {}

        url = f"{get_base_url(self.git_repository)}/pullRequests/{pull_request_source_id}/threads"

        self.logger.info(f"Getting comments for {pull_request_source_id}")
        data = await async_fetch(
            url,
            client=self.client,  # headers=get_header(self.git_repository), timeout=None
        )

        authors_to_exclude = filters.get("authors_to_exclude", [])
        comments = []

        for thread in data["value"]:
            for comment in thread["comments"]:
                if comment["commentType"] == "text":
                    author = comment["author"]["displayName"]
                    email = comment["author"]["uniqueName"]
                    if author in authors_to_exclude:
                        continue

                    comments.append(
                        Comment.from_dict(
                            {
                                "pull_request_id": pull_request_source_id,
                                "creation_date": comment.get("publishedDate"),
                                "content": comment.get("content"),
                                "developer": {
                                    "full_name": author,
                                    "email": email,
                                },
                            }
                        )
                    )

        return comments

    @monitor("extracting pull_requests")
    async def find_all(self, options=None):
        filters = options or {}

        pull_requests = filters.get("pull_requests")
        pull_request = filters.get("pull_request")
        if pull_request:
            pull_requests = [pull_request]

        pull_requests = [
            pr.source_id if isinstance(pr, PullRequest) else pr for pr in pull_requests
        ]

        if not pull_requests:
            raise Exception("No pull request provided")

        async with aiohttp.ClientSession(
            headers=get_header(self.git_repository),
        ) as client:
            self.client = client
            result = await self.__fetch_comments_for_pull_requests.run_all(
                self, [(pull_request, options) for pull_request in pull_requests]
            )

        return list(itertools.chain.from_iterable(result))
