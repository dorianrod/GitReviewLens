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

    def upsert(self, entity: _T, options: Optional[_U] = None):
        raise NotImplementedError("Not used yet")

    def create(self, entity: _T, options: Optional[_U] = None):
        self.upsert(entity, {**(options or {}), "is_new": True})  # type: ignore

    def update(self, entity: _T, options: Optional[_U] = None):
        self.upsert(entity, {**(options or {}), "is_new": False})  # type: ignore

    def create_all(self, entities: Sequence[_T]) -> None:
        for entity in entities:
            self.create(entity)

    def update_all(self, entities: Sequence[_T]) -> None:
        for entity in entities:
            self.update(entity)

    def upsert_all(self, entities: Sequence[_T], options: Optional[_U] = None) -> None:
        for entity in entities:
            self.upsert(entity, options)

    def get_by_id(self, id: str) -> _T | None:
        item = self.find_all({"id": id})  # type: ignore
        if len(item) == 0:
            raise NotExistsException(f"Item with id {id} does not exist")

        return item[0]

    def find_all(self, filters: Optional[_F] = None) -> Sequence[_T]:
        raise NotImplementedError("Not used yet")
