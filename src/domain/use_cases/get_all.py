from dataclasses import dataclass
from typing import Sequence, TypeVar

from src.common.repositories.base_repository import BaseRepository
from src.common.use_cases.base_use_case import BaseUseCase

_T = TypeVar("_T")


@dataclass
class GetAllUseCase(BaseUseCase[Sequence[_T]]):
    repository: BaseRepository

    def execute(self) -> Sequence[_T]:
        return self.repository.find_all()
