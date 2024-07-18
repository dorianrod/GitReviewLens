from dataclasses import dataclass

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
