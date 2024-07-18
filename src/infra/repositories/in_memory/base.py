from typing import Generic, TypeVar

from src.domain.entities.common import BaseEntity
from src.domain.exceptions import NotExistsException

_T = TypeVar("_T", bound=BaseEntity)


class BaseInMemoryRepositoryMixin(Generic[_T]):
    entities_by_ids: dict[str, _T]

    def __init__(self, *args, **kwargs):
        self.entities_by_ids = {}
        super().__init__(*args, **kwargs)

    async def find_all(self, options=None):
        return list(self.entities_by_ids.values())

    async def get_by_id(self, id: str):
        entity = self.entities_by_ids.get(id)
        if not entity:
            raise NotExistsException()

        return entity

    async def upsert(self, entity: _T, options=None):
        if entity.id:
            self.entities_by_ids[entity.id] = entity
