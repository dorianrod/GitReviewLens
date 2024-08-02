import itertools

import aiohttp

from src.common.utils.worker import concurrency_aio
from src.domain.entities.comment import Comment
from src.domain.repositories.comments import CommentsRepository
from src.infra.repositories.azure.utils import get_base_url, get_header
from src.infra.requests.fetch import async_fetch


class CommentsAzureRepository(CommentsRepository):
    @concurrency_aio(max_concurrency=50)
    async def __fetch_comments_for_pull_requests(self, pr_ids, filters):
        filters = filters or {}

        pull_request_source_id, pull_request_id = pr_ids

        url = f"{get_base_url(self.git_repository)}/pullRequests/{pull_request_source_id}/threads"

        self.logger.info(f"Getting comments for {pull_request_source_id}")
        data = await async_fetch(
            url,
            client=self.client,
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
                                "pull_request_id": pull_request_id,
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

    async def find_all(self, filters=None):
        pull_requests_ids = self._get_pull_requests_from_options(filters)

        async with aiohttp.ClientSession(
            headers=get_header(self.git_repository),
        ) as client:
            self.client = client
            result = await self.__fetch_comments_for_pull_requests.run_all(
                self, [(ids, filters) for ids in pull_requests_ids]
            )

        return list(itertools.chain.from_iterable(result))
