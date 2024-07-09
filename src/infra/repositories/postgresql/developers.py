from dataclasses import dataclass

from src.common.monitoring.logger import LoggerInterface
from src.domain.repositories.developers import DeveloperRepository
from src.infra.database.postgresql.models.models import Developer as DeveloperModel
from src.infra.repositories.postgresql.generic_db import GenericDatabaseRepository


@dataclass
class DeveloperDatabaseRepository(GenericDatabaseRepository, DeveloperRepository):
    logger: LoggerInterface
    Model = DeveloperModel
