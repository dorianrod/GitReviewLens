import requests

from src.domain.entities.comment import Comment
from src.domain.repositories.comments import CommentsRepository
from src.infra.repositories.github.utils import get_base_url, get_email, get_header


class CommentsGithubRepository(CommentsRepository):
    max_results: int
    use_pagination: bool = True

    def __init__(self, *args, **kwargs):
        self.max_results = kwargs.pop("max_results") if "max_results" in kwargs else 100
        super().__init__(*args, **kwargs)

    async def _get_all_comments(self, pull_request_id, page=1):
        results = []

        url = f"{get_base_url(self.git_repository)}/pulls/{pull_request_id}/comments?per_page={self.max_results}&page={page}"

        response = requests.get(url, headers=get_header(self.git_repository))
        if response.status_code != 200:
            raise Exception(
                f"Unable to get comments in Github: {str(response.content)}"
            )

        comments_from_github = response.json()
        results += comments_from_github

        if self.use_pagination and len(comments_from_github) == self.max_results:
            results += await self._get_all_comments(
                page=page + 1, pull_request_id=pull_request_id
            )

        return results

    async def find_all(self, filters=None):
        pull_request = filters.get("pull_request")
        if not pull_request:
            raise Exception("No pull request provided")

        comments_from_github = await self._get_all_comments(
            pull_request_id=pull_request.source_id
        )
        authors_to_exclude = filters.get("authors_to_exclude", [])
        comments = []

        for comment in comments_from_github:
            author = comment["user"]["login"]
            email = get_email(author)
            if author in authors_to_exclude:
                continue

            comments.append(
                Comment.from_dict(
                    {
                        "creation_date": comment["created_at"],
                        "content": comment["body"],
                        "developer": {
                            "full_name": author,
                            "email": email,
                        },
                    }
                )
            )

        return comments
