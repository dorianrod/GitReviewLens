from abc import abstractmethod
from datetime import datetime
from typing import Any

from src.common.utils.date import set_tz_if_not_set
from src.common.utils.json import recursive_asdict


def eq(self, other):
    if isinstance(other, self.__class__):
        cur_dict = self.to_dict()
        other_dict = other.to_dict()
        return cur_dict == other_dict
    return False


class BaseEntity(object):
    @property
    @abstractmethod
    def id(self):
        pass

    def __setattr__(self, name, value):
        if isinstance(value, datetime):
            value = set_tz_if_not_set(value)
        super().__setattr__(name, value)

    def __hash__(self):
        return hash((self.id, self.__class__.__name__))

    def __eq__(self, other):
        return eq(self, other)

    def clone(self):
        return self.__class__.from_dict(self.to_dict())

    def to_dict(self):
        return recursive_asdict(self)

    def from_dict(self, values: dict[str, Any] = {}):
        raise NotImplementedError()
