from dataclasses import dataclass

from src.common.utils.json import recursive_asdict
from src.domain.entities.common import BaseEntity


@dataclass
class Transcoder(BaseEntity):
    name: str | None
    values: dict[str, str]

    @classmethod
    def from_dict(cls, data):
        return cls(name=data["name"], values=(data.get("values") or {}).copy())

    def to_dict(self):
        transcoder_dict = recursive_asdict(self)
        return transcoder_dict

    def transcode(self, value):
        if value in self.values:
            return self.values.get(value)

        if "" in self.values:
            return self.values.get("")

        return value

    def transcode_by_startvalue(self, value):
        if value is None:
            return value

        for key in self.values:
            if value != "" and key != "" and value.startswith(key):
                return self.values.get(key)

        if "" in self.values:
            return self.values.get("")

        return value
