from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

_R = TypeVar("_R")


class BaseUseCaseWithParameters(ABC, Generic[_R]):
    @abstractmethod
    async def execute(self, *args: Any, **kwargs: Any) -> _R:
        raise NotImplementedError()


class BaseUseCase(ABC, Generic[_R]):
    @abstractmethod
    async def execute(self) -> _R:
        raise NotImplementedError()
