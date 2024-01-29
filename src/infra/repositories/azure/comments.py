import requests

from src.domain.entities.comment import Comment
from src.domain.repositories.comments import CommentsRepository
from src.infra.repositories.azure.utils import get_base_url, get_header


class CommentsAzureRepository(CommentsRepository):
    def find_all(self, filters=None):
        filters = filters or {}

        pull_request = filters.get("pull_request")
        if not pull_request:
            raise Exception("No pull request provided")

        url = f"{get_base_url(self.git_repository)}/pullRequests/{pull_request.source_id}/threads"

        response = requests.get(url, headers=get_header(self.git_repository))
        if response.status_code != 200:
            raise Exception(
                f"Unable to get pull requests in Azure: {str(response.content)}"
            )

        authors_to_exclude = filters.get("authors_to_exclude", [])
        comments = []

        data = response.json()
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
