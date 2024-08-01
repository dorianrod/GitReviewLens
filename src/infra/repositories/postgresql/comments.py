from sqlalchemy import select
from sqlalchemy.orm import joinedload

from src.domain.repositories.comments import CommentsRepository
from src.infra.database.postgresql.models.models import Comment as CommentModel
from src.infra.repositories.postgresql.generic_db import GenericDatabaseRepository
from src.infra.repositories.postgresql.upsert_all_developers import (
    UpsertAllDevelopersMixin,
)


class CommentsDatabaseRepository(
    GenericDatabaseRepository, CommentsRepository, UpsertAllDevelopersMixin
):
    Model = CommentModel

    async def upsert_all(self, entities, options=None) -> None:
        if not entities:
            return

        try:
            is_new = options.pop("is_new")
        except KeyError:
            is_new = None

        await self.upsert_all_developers(entities, options)

        await self._upsert_all_entities_within_transaction(
            entities, {**options, "is_new": is_new}
        )

    async def _select_find_all(self, session, filters=None):
        Model = self.Model

        filters = filters or {}

        pull_request = filters.get("pull_request")
        if not pull_request:
            raise NotImplementedError()

        return (
            select(Model)
            .options(joinedload(Model.developer))
            .filter(Model.pull_request_id == pull_request.id)
        )
