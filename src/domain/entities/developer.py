from dataclasses import dataclass
from typing import Sequence

from src.domain.entities.common import BaseEntity


@dataclass(frozen=True)
class Developer(BaseEntity):
    full_name: str
    email: str

    @property
    def id(self):
        return self.email

    @classmethod
    def from_dict(cls, data):
        return cls(full_name=data.get("full_name"), email=data.get("email"))

    def to_dict(self):
        return {
            "full_name": self.full_name,
            "email": self.email,
            "id": self.id,
        }

    def __repr__(self):
        return f"<Developer {self.email} - {self.full_name}>"

    @staticmethod
    def unduplicate(developers: Sequence['Developer']) -> set['Developer']:
        developers_id_set: set[Developer] = set()
        developers_set: set[Developer] = set()
        for developer in developers:
            if developer.id not in developers_id_set:
                developers_id_set.add(developer.id)
                developers_set.add(developer)
        return developers_set
