from src.common.monitoring.logger import LoggerInterface
from src.domain.entities.developer import Developer
from src.domain.repositories.developers import DeveloperRepository


class DevelopersInMemoryRepository(DeveloperRepository):
    developers: dict[str, Developer] = {}

    def __init__(self, logger: LoggerInterface):
        super().__init__(logger)
        self.developers: dict[str, Developer] = {}

    async def find_all(self):
        return list(self.developers.values())

    async def get_by_id(self, id: str):
        return self.developers.get(id)

    async def upsert(self, developer: Developer, options=None):
        self.developers[developer.id] = developer
