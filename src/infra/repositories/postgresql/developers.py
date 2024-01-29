from dataclasses import dataclass

from src.common.monitoring.logger import LoggerInterface
from src.domain.entities.developer import Developer
from src.domain.repositories.developers import DeveloperRepository
from src.infra.database.postgresql.database import get_db_session
from src.infra.database.postgresql.models.models import Developer as DeveloperModel
from src.infra.repositories.postgresql.utils import (
    raise_exception_if_upsert_cannot_be_done,
)


@dataclass
class DeveloperDatabaseRepository(DeveloperRepository):
    logger: LoggerInterface

    def _get_model_by_id(self, entity: Developer) -> DeveloperModel:
        session = get_db_session()
        developer = (
            session.query(DeveloperModel).filter(DeveloperModel.id == entity.id).first()
        )
        return developer

    def upsert(self, entity, options=None):
        options = options or {}

        developer = self._get_model_by_id(entity)

        raise_exception_if_upsert_cannot_be_done(options, developer)

        session = get_db_session()

        if developer is not None:
            self.logger.info(f"Updating developer: {repr(entity)}")
            developer.name = entity.full_name
        else:
            self.logger.info(f"Creating developer: {repr(entity)}")
            columns = DeveloperModel.from_entity(entity)
            developer = DeveloperModel(**columns)

        session.add(developer)
        session.commit()

    def find_all(self, filters=None):
        session = get_db_session()
        developers_data = list(
            session.query(DeveloperModel.name, DeveloperModel.email).all()
        )
        developers = [
            DeveloperModel.to_entity(developer) for developer in developers_data
        ]
        return developers

    def get_by_id(self, id):
        session = get_db_session()
        developers_data = session.query(DeveloperModel.name, DeveloperModel.email).get(
            id
        )
        developer = DeveloperModel.to_entity(developers_data)
        return developer
