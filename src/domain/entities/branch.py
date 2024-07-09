import json
from dataclasses import dataclass
from typing import Any

from src.domain.entities.common import BaseEntity
from src.domain.entities.repository import Repository


@dataclass
class Branch(BaseEntity):
    name: str
    repository: Repository

    @property
    def id(self):
        return self.name

    @staticmethod
    def parse(config: dict | str | Any) -> 'Branch':
        if isinstance(config, str):
            return Branch.__from_str(config)
        if isinstance(config, dict):
            return Branch.__from_dict(config)
        if isinstance(config, Branch):
            return config

        raise Exception("Configuration format is not ok")

    @staticmethod
    def __from_dict(config: dict) -> 'Branch':
        return Branch(
            name=config.get("name") or "",
            repository=Repository.parse(config.get("repository")),
        )

    @classmethod
    def __from_str(cls, config: str) -> 'Branch':
        try:
            options = json.loads(config)
            name = options["name"]
            repository = options["repository"]
        except Exception:
            name = config.split(":")[-1]
            repository = ":".join(config.split(":")[0:-1])

        return cls.__from_dict({"name": name, "repository": repository})
