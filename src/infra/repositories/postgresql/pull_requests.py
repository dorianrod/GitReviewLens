from sqlalchemy import delete, insert, select
from sqlalchemy.orm import joinedload, subqueryload
from src.domain.repositories.pull_requests import PullRequestsRepository
from src.domain.repositories.utils import (
    raise_exception_if_repository_differs_from_entity,
)
from src.infra.database.postgresql.database import start_transaction
from src.infra.database.postgresql.models.models import PullRequest as PullRequestModel
from src.infra.repositories.postgresql.comments import CommentsDatabaseRepository
from src.infra.repositories.postgresql.generic_db import GenericDatabaseRepository
from src.infra.repositories.postgresql.upsert_all_developers import (
    UpsertAllDevelopersMixin,
)


class PullRequestsDatabaseRepository(
    PullRequestsRepository, GenericDatabaseRepository, UpsertAllDevelopersMixin
):
    Model = PullRequestModel

    async def upsert_all_pull_request(self, entities, options=None):
        options = options or {}

        async with start_transaction() as session:
            SqlEntity = self.Model
            pull_request_approvers = self.Model.models["pull_request_approvers"]

            # Data preparation
            pull_requests_mappings = []
            approver_mappings = []
            pull_request_ids = []
            for entity in entities:
                pull_request_ids.append(entity.id)
                pull_requests_mappings.append(SqlEntity.from_entity(entity, options))
                for approver in entity.approvers:
                    approver_mappings.append(
                        {"pull_request_id": entity.id, "approver_id": approver.id}
                    )

            self.logger.info(f"Upserting {len(pull_request_ids)} pull_requests")

            # Pull requests
            await self._upsert_entities_in_bulk(session, entities, options)

            # Approvers
            if pull_request_ids:
                delete_stmt = delete(pull_request_approvers).where(
                    pull_request_approvers.c.pull_request_id.in_(pull_request_ids)
                )
                await session.execute(delete_stmt)
            if approver_mappings:
                insert_stmt = insert(pull_request_approvers)
                await session.execute(insert_stmt, approver_mappings)

            await session.commit()

    async def upsert_all_comments(self, entities, options=None) -> None:
        options = options or {}
        upsert_comments = options.get("upsert_comments", True)

        if upsert_comments and len(entities):
            comment_repository = CommentsDatabaseRepository(
                logger=self.logger, git_repository=self.git_repository
            )
            comments = entities[0].get_comments_from_list(entities)
            await comment_repository.upsert_all(
                comments,
                {
                    "upsert_pull_request": False,
                    "upsert_developers": False,
                },
            )

    async def upsert_all(self, entities, options=None) -> None:
        if not entities:
            return

        try:
            options = options or {}
            is_new = options.pop("is_new")
        except KeyError:
            is_new = None

        raise_exception_if_repository_differs_from_entity(
            self.git_repository, entities[0]
        )

        await self.upsert_all_developers(entities, options)
        await self.upsert_all_pull_request(entities, {**options, "is_new": is_new})
        await self.upsert_all_comments(entities, {**options, "is_new": is_new})

    async def _select_find_all(self, session, options=None):
        filters = options or {}

        Model = self.Model
        CommentModel = self.Model.models["Comment"]

        query = (
            select(Model)
            .options(
                joinedload(Model.created_by),
                subqueryload(Model.comments).joinedload(CommentModel.developer),
                subqueryload(Model.approvers),
            )
            .filter(Model.repository == self.git_repository.path)
        )

        pull_request_source_id = filters.get("source_id")
        pull_request_id = filters.get("id")
        if pull_request_id:
            query = query.filter(Model.id == pull_request_id)
        elif pull_request_source_id:
            query.filter(Model.source_id == pull_request_source_id)

        return query
