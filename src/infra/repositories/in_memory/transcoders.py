from src.domain.entities.transcoder import Transcoder
from src.domain.repositories.transcoders import TranscodersRepository
from src.infra.repositories.in_memory.base import BaseInMemoryRepositoryMixin


class TranscodersInMemoryRepository(
    BaseInMemoryRepositoryMixin[Transcoder], TranscodersRepository
):
    async def get_by_id(self, id: str):
        try:
            return await super().get_by_id(id)
        except Exception:
            return Transcoder(None, {})
