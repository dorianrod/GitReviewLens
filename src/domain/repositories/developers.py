from dataclasses import dataclass
from typing import Optional

from src.common.monitoring.logger import LoggerInterface
from src.common.repositories.base_repository import BaseRepository
from src.domain.entities.developer import Developer


@dataclass
class DeveloperRepository(BaseRepository[Developer, Optional[dict], Optional[dict]]):
    logger: LoggerInterface

    async def upsert(self, entity: Developer, options: dict | None = None):
        pass
