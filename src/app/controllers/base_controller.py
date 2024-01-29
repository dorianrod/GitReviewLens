from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Generic, TypeVar

from src.common.monitoring.logger import LoggerInterface

_T = TypeVar("_T")
_R = TypeVar("_R")


@dataclass
class BaseController(ABC, Generic[_T, _R]):
    logger: LoggerInterface

    @abstractmethod
    def execute(self, args: _T):
        pass
