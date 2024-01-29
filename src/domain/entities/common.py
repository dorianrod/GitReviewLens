from abc import ABC
from datetime import datetime
from typing import Any

from src.common.utils.date import set_tz_if_not_set
from src.common.utils.json import recursive_asdict


class BaseEntity(ABC):
    def __setattr__(self, name, value):
        if isinstance(value, datetime):
            value = set_tz_if_not_set(value)
        super().__setattr__(name, value)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.to_dict() == other.to_dict()
        return False

    def clone(self):
        return self.__class__.from_dict(self.to_dict())

    def to_dict(self):
        return recursive_asdict(self)

    def from_dict(self, values: dict[str, Any] = {}):
        raise NotImplementedError()
