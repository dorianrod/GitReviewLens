from src.domain.entities.comment import Comment
from src.domain.entities.pull_request import PullRequest
from src.domain.repositories.comments import CommentsRepository
from src.infra.database.postgresql.database import get_db_session
from src.infra.database.postgresql.models.models import Comment as CommentModel
from src.infra.repositories.postgresql.utils import (
    raise_exception_if_upsert_cannot_be_done,
)


class CommentsDatabaseRepository(CommentsRepository):
    async def upsert(self, entity: Comment, options=None) -> None:
        options = options or {}

        pull_request: PullRequest = options.get("pull_request")

        await super().upsert(entity, options)

        from src.infra.repositories.postgresql.developers import (
            DeveloperDatabaseRepository,
        )
        from src.infra.repositories.postgresql.pull_requests import (
            PullRequestsDatabaseRepository,
        )

        upsert_developer = options.get("upsert_developer", True)
        upsert_pull_request = options.get("upsert_pull_request", True)

        session = get_db_session()

        columns = CommentModel.from_entity(entity, pull_request)

        comment = (
            session.query(CommentModel)
            .filter(
                CommentModel.id == columns["id"],
            )
            .first()
        )

        raise_exception_if_upsert_cannot_be_done(options, comment)

        if upsert_developer:
            repository_developer = DeveloperDatabaseRepository(logger=self.logger)
            await repository_developer.upsert(entity.developer)

        if upsert_pull_request:
            repository_pull_request = PullRequestsDatabaseRepository(
                logger=self.logger,
                git_repository=self.git_repository,
            )
            await repository_pull_request.upsert(
                pull_request, {"upsert_comments": False}
            )

        self.logger.debug(f"Creating {repr(entity)}")

        if comment is not None:
            for key in columns:
                setattr(comment, key, columns[key])
        else:
            comment = CommentModel(**columns)

        session.add(comment)
        session.commit()

    async def find_all(self, filters=None):
        filters = filters or {}

        pull_request = filters.get("pull_request")
        if not pull_request:
            raise NotImplementedError()

        session = get_db_session()
        entities = (
            session.query(CommentModel)
            .filter(
                CommentModel.pull_request_id == pull_request.id,
            )
            .all()
        )
        return [CommentModel.to_entity(entity) for entity in entities]
