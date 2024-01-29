from src.common.monitoring.logger import LoggerInterface
from src.domain.entities.transcoder import Transcoder
from src.domain.repositories.transcoders import TranscodersRepository


class TranscodersInMemoryRepository(TranscodersRepository):
    transcoders: dict[str, Transcoder]

    def __init__(self, logger: LoggerInterface):
        super().__init__(logger)
        self.transcoders: dict[str, Transcoder] = {}

    def find_all(self):
        return list(self.transcoders.values())

    def get_by_id(self, id: str):
        return self.transcoders.get(id, Transcoder(None, {}))

    def upsert(self, entity: Transcoder, options=None):
        if entity.name:
            self.transcoders[entity.name] = entity
