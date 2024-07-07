import asyncio
from abc import ABC
from typing import Generic, Optional, Sequence, TypeVar

from src.common.monitoring.logger import LoggerInterface
from src.domain.exceptions import NotExistsException

_T = TypeVar("_T")
_F = TypeVar("_F")
_U = TypeVar("_U")


class BaseRepository(ABC, Generic[_T, _F, _U]):
    """
    Abstract generic Repository
    """

    logger: LoggerInterface

    async def upsert(self, entity: _T, options: Optional[_U] = None):
        raise NotImplementedError("Not used yet")

    async def create(self, entity: _T, options: Optional[_U] = None):
        await self.upsert(entity, {**(options or {}), "is_new": True})  # type: ignore

    async def update(self, entity: _T, options: Optional[_U] = None):
        await self.upsert(entity, {**(options or {}), "is_new": False})  # type: ignore

    async def create_all(self, entities: Sequence[_T]) -> None:
        tasks = [self.create(entity) for entity in entities]
        await asyncio.gather(*tasks)

    async def update_all(self, entities: Sequence[_T]) -> None:
        tasks = [self.update(entity) for entity in entities]
        await asyncio.gather(*tasks)

    async def upsert_all(
        self, entities: Sequence[_T], options: Optional[_U] = None
    ) -> None:
        tasks = [self.upsert(entity) for entity in entities]
        await asyncio.gather(*tasks)

    async def get_by_id(self, id: str) -> _T | None:
        item = await self.find_all({"id": id})  # type: ignore
        if len(item) == 0:
            raise NotExistsException(f"Item with id {id} does not exist")

        return item[0]

    async def find_all(self, filters: Optional[_F] = None) -> Sequence[_T]:
        raise NotImplementedError("Not used yet")
