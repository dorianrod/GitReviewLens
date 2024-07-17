from sqlalchemy import select
from sqlalchemy.orm import joinedload, subqueryload

from src.domain.entities.pull_request import PullRequest
from src.domain.repositories.pull_requests import PullRequestsRepository
from src.infra.database.postgresql.database import get_db_session
from src.infra.database.postgresql.models.models import PullRequest as PullRequestModel
from src.infra.database.postgresql.models.models import pull_request_approvers
from src.infra.repositories.postgresql.comments import CommentsDatabaseRepository
from src.infra.repositories.postgresql.developers import DeveloperDatabaseRepository
from src.infra.repositories.postgresql.generic_db import GenericDatabaseRepository


class PullRequestsDatabaseRepository(GenericDatabaseRepository, PullRequestsRepository):
    Model = PullRequestModel

    async def _update_approvers(self, entity):
        async with get_db_session() as session:
            async with session.begin():
                try:
                    await session.execute(
                        pull_request_approvers.delete().where(
                            pull_request_approvers.c.pull_request_id == entity.id
                        )
                    )
                    for approver in entity.approvers:
                        await session.execute(
                            pull_request_approvers.insert().values(
                                pull_request_id=entity.id,
                                approver_id=approver.id,
                            )
                        )
                    await session.commit()
                except Exception as e:
                    print(e)
                    raise e

    async def upsert(self, entity: PullRequest, options=None):
        options = options or {}

        upsert_developers = options.get("upsert_developers", True)
        upsert_comments = options.get("upsert_comments", True)

        if upsert_developers:
            developer_repository = DeveloperDatabaseRepository(logger=self.logger)
            developers = entity.get_developers()
            await developer_repository.upsert_all(developers)

        await super().upsert(entity, {**options, "many_to_many": False})

        await self._update_approvers(entity)

        if upsert_comments:
            comment_repository = CommentsDatabaseRepository(
                logger=self.logger, git_repository=self.git_repository
            )
            await comment_repository.upsert_all(
                entity.comments,
                {
                    "pull_request": entity,
                    "upsert_pull_request": False,
                    "upsert_developers": False,
                },
            )

    async def _select_find_all(self, session, options=None):
        filters = options or {}

        query = (
            select(PullRequestModel)
            .options(
                joinedload(PullRequestModel.created_by),
                subqueryload(PullRequestModel.comments),
                subqueryload(PullRequestModel.approvers),
            )
            .filter(PullRequestModel.repository == self.git_repository.path)
        )

        pull_request_source_id = filters.get("source_id")
        pull_request_id = filters.get("id")
        if pull_request_id:
            query = query.filter(PullRequestModel.id == pull_request_id)
        elif pull_request_source_id:
            query.filter(PullRequestModel.source_id == pull_request_source_id)

        return query
