from src.common.monitoring.logger import LoggerInterface


class UpsertAllDevelopersMixin:
    logger: LoggerInterface

    async def upsert_all_developers(self, entities, options=None) -> None:
        options = options or {}
        upsert_developers = options.get("upsert_developers", True)

        if upsert_developers and len(entities):
            from src.infra.repositories.postgresql.developers import (
                DeveloperDatabaseRepository,
            )

            entity = entities[0]
            developers = entity.get_developers_from_list(entities)
            developer_repository = DeveloperDatabaseRepository(logger=self.logger)
            self.logger.info(
                f"Upsert {len(developers)} developers related to {len(entities)} pull requests"
            )
            await developer_repository.upsert_all(developers)
