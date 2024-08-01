from typing import Type

from sqlalchemy import select

from src.common.repositories.base_repository import BaseRepository
from src.domain.exceptions import NotExistsException
from src.infra.database.postgresql.database import get_db_session
from src.infra.database.postgresql.models.models import BaseModel
from src.infra.repositories.postgresql.upsert_entity_in_bulk import UpsertEntityInBulk


class GenericDatabaseRepository(UpsertEntityInBulk, BaseRepository):
    Model: Type[BaseModel]

    async def upsert(self, entity, options=None):
        await self.upsert_all([entity], options)

    async def find_all(self, options=None):
        async with get_db_session() as session:  # start_transaction?
            query = await self._select_find_all(session, options)
            result = await session.execute(query)
            rows = result.scalars().all()
            entities = []
            for row in rows:
                entities.append(self.Model.to_entity(row))

        return entities

    async def get_by_id(self, id):
        async with get_db_session() as session:
            query = await self._select_find_all(session, {"id": id})
            result = await session.execute(query)
            row = result.scalar_one_or_none()

            if not row:
                raise NotExistsException

            entity = self.Model.to_entity(row)
            return entity

    async def _select_find_all(self, session, filters=None):
        filters = filters or {}

        query = select(self.Model)

        id = filters.get("id")
        if id:
            query = query.filter(self.Model.id == id)

        return query
