from abc import abstractmethod
from dataclasses import dataclass
from typing import Sequence

from src.common.monitoring.logger import LoggerInterface
from src.common.repositories.base_repository import BaseRepository
from src.domain.entities.transcoder import Transcoder


@dataclass
class TranscodersRepository(BaseRepository[Transcoder, dict, dict]):
    logger: LoggerInterface

    @abstractmethod
    def find_all(self, options=None) -> Sequence[Transcoder]:
        pass

    @abstractmethod
    def get_by_id(self, id: str) -> Transcoder:
        pass
