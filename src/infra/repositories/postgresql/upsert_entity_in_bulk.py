from typing import Type

from sqlalchemy import select

from src.common.monitoring.logger import LoggerInterface
from src.infra.database.postgresql.database import start_transaction
from src.infra.database.postgresql.lock import lock_manager
from src.infra.database.postgresql.models.models import BaseModel


class IntegrityError(Exception):
    pass


class DoesNotExistError(Exception):
    pass


class UpsertEntityInBulk:
    Model: Type[BaseModel]
    logger: LoggerInterface

    async def upsert_all(self, entities, options=None):
        await self._upsert_all_entities_within_transaction(entities, options)

    async def _upsert_all_entities_within_transaction(self, entities, options=None):
        if not entities:
            return

        async with lock_manager.lock(*entities):
            async with start_transaction() as session:
                await self._upsert_entities_in_bulk(
                    entities=entities, session=session, options=options
                )
                await session.commit()

    async def _fetch_existing_entity_ids(self, session, entity_ids):
        SqlEntity = self.Model

        query = select(SqlEntity.id).filter(SqlEntity.id.in_(list(entity_ids)))
        result = await session.execute(query)
        return set([row[0] for row in result.fetchall()])

    async def _upsert_entities_in_bulk(self, session, entities, options=None) -> None:
        options = options or {}
        is_new = options.get("is_new")

        entity_ids = set([entity.id for entity in entities])
        existing_ids = await self._fetch_existing_entity_ids(session, entity_ids)

        SqlEntity = self.Model
        mapping_insertions = []
        mapping_updates = []
        for entity in entities:
            data = SqlEntity.from_entity(entity, options)
            if entity.id in existing_ids:
                mapping_updates.append(data)
            else:
                mapping_insertions.append(data)

        self.logger.info(
            f"Upserting {len(mapping_insertions) + len(mapping_updates)} {SqlEntity.__tablename__}"
        )

        if is_new is True and mapping_updates:
            raise DoesNotExistError(
                "Some entities does not exist and cannot be updated"
            )

        if is_new is False and mapping_insertions:
            raise IntegrityError("Some entities already exist and cannot be inserted")

        if mapping_insertions:
            await session.run_sync(
                lambda session: session.bulk_insert_mappings(
                    SqlEntity, mapping_insertions
                )
            )

        if mapping_updates:
            await session.run_sync(
                lambda session: session.bulk_update_mappings(SqlEntity, mapping_updates)
            )
