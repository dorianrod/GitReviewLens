from datetime import datetime

from src.common.utils.date import are_dates_equal
from src.domain.entities.comment import Comment
from src.domain.entities.pull_request import PullRequest


class CommentMixin:
    async def test_it_creates_comment(
        self,
        comment_repository,
        pull_request_repository,
        fixture_comment_dict,
        fixture_pull_request_dict,
    ):
        pull_request = PullRequest.from_dict(fixture_pull_request_dict)
        pull_request.comments = []
        await pull_request_repository.create(pull_request)

        comment = Comment.from_dict(fixture_comment_dict)
        comment.creation_date = datetime.now()
        comment.pull_request_id = pull_request.id

        await comment_repository.create(comment)

        created_comments = await comment_repository.find_all(
            {"pull_request": pull_request}
        )
        assert len(created_comments) == 1

        created_comment = created_comments[0]
        assert comment.developer.id == created_comment.developer.id
        assert comment.content == created_comment.content
        assert are_dates_equal(comment.creation_date, created_comment.creation_date)

    async def test_can_create_same_comments_for_different_repo(
        self,
        comment_repository,
        comment_repository_2,
        fixture_comment_dict,
        fixture_pull_request_dict,
        pull_request_repository,
        pull_request_repository_2,
    ):
        pull_request = PullRequest.from_dict(
            {**fixture_pull_request_dict, "comments": []}
        )
        await pull_request_repository.upsert(pull_request)

        pull_request_from_another_repo = PullRequest.from_dict(
            {
                **fixture_pull_request_dict,
                "comments": [],
                "git_repository": pull_request_repository_2.git_repository,
            }
        )
        await pull_request_repository_2.upsert(pull_request_from_another_repo)

        comment_1 = Comment.from_dict(
            {**fixture_comment_dict, "pull_request_id": pull_request.id}
        )
        await comment_repository.create(comment_1)

        comment_2 = Comment.from_dict(
            {
                **fixture_comment_dict,
                "pull_request_id": pull_request_from_another_repo.id,
            }
        )
        await comment_repository_2.create(comment_2)

        comments_1 = await comment_repository.find_all({"pull_request": pull_request})
        assert comments_1 == [comment_1]
        assert await comment_repository_2.find_all(
            {"pull_request": pull_request_from_another_repo}
        ) == [comment_2]
