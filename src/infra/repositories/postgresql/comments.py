from sqlalchemy import select
from sqlalchemy.orm import joinedload

from src.domain.entities.comment import Comment
from src.domain.entities.pull_request import PullRequest
from src.domain.repositories.comments import CommentsRepository
from src.infra.database.postgresql.models.models import Comment as CommentModel
from src.infra.repositories.postgresql.generic_db import GenericDatabaseRepository


class CommentsDatabaseRepository(
    GenericDatabaseRepository,
    CommentsRepository,
):
    Model = CommentModel

    async def upsert(self, entity: Comment, options=None) -> None:
        options = options or {}

        pull_request: PullRequest = options.get("pull_request")

        upsert_developer = options.get("upsert_developer", True)
        upsert_pull_request = options.get("upsert_pull_request", True)

        if upsert_developer:
            from src.infra.repositories.postgresql.developers import (
                DeveloperDatabaseRepository,
            )

            repository_developer = DeveloperDatabaseRepository(logger=self.logger)
            await repository_developer.upsert(entity.developer)

        if upsert_pull_request:
            from src.infra.repositories.postgresql.pull_requests import (
                PullRequestsDatabaseRepository,
            )

            repository_pull_request = PullRequestsDatabaseRepository(
                logger=self.logger,
                git_repository=self.git_repository,
            )
            await repository_pull_request.upsert(
                pull_request, {"upsert_comments": False}
            )

        self.logger.debug(f"Creating {repr(entity)}")
        await super().upsert(entity, options)

    async def _select_find_all(self, session, options=None):
        filters = options or {}

        pull_request = filters.get("pull_request")
        if not pull_request:
            raise NotImplementedError()

        return (
            select(CommentModel)
            .options(joinedload(CommentModel.developer))
            .filter(CommentModel.pull_request_id == pull_request.id)
        )
