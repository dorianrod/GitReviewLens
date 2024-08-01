from typing import Type

from src.common.monitoring.logger import LoggerInterface
from src.infra.database.postgresql.models.models import BaseModel


class UpsertAllDevelopersMixin:
    logger: LoggerInterface
    Model: Type[BaseModel]

    async def upsert_all_developers(self, entities, options=None) -> None:
        options = options or {}
        upsert_developers = options.get("upsert_developers", True)

        if upsert_developers and len(entities):
            from src.infra.repositories.postgresql.developers import (
                DeveloperDatabaseRepository,
            )

            SqlEntity = self.Model

            entity = entities[0]
            developers = entity.get_developers_from_list(entities)
            developer_repository = DeveloperDatabaseRepository(logger=self.logger)
            self.logger.info(
                f"Upsert {len(developers)} developers related to {len(entities)} {SqlEntity.__tablename__}"
            )
            await developer_repository.upsert_all(developers)
