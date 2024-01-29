import json
from dataclasses import dataclass
from typing import Any

from src.domain.entities.common import BaseEntity
from src.domain.entities.types import RepositoryType, RepositoryTypes


@dataclass
class Repository(BaseEntity):
    organisation: str | None
    project: str | None
    url: str | None
    name: str
    token: str | None = None

    def __str__(self):
        return self.path

    @property
    def type(self) -> RepositoryType | None:
        if not self.url:
            return None

        if "github.com" in self.url:
            return RepositoryTypes.GITHUB
        if "azure.com" in self.url:
            return RepositoryTypes.AZURE

        return None

    @property
    def path(self):
        return (
            f"{self.organisation}/{self.project}/{self.name}"
            if self.organisation and self.project
            else f"{self.organisation or self.project}/{self.name}"
        )

    @classmethod
    def parse(cls, config: dict | str | Any) -> 'Repository':
        if isinstance(config, str):
            return cls.__from_str(config)
        if isinstance(config, dict):
            return cls.__from_dict(config)
        if isinstance(config, Repository):
            return config

        raise Exception("Configuration format is not ok")

    @classmethod
    def __from_dict(cls, config: dict[str, str | None]) -> 'Repository':
        return cls(
            url=config.get("url"),
            organisation=config.get("organisation"),
            project=config.get("project"),
            name=config.get("name") or "",
            token=config.get("token"),
        )

    @classmethod
    def __from_str(cls, config: str) -> 'Repository':
        try:
            options = json.loads(config)
            url = options["url"]
            organisation = options["organisation"]
            project = options["project"]
            name = options["name"]
            token = options["token"]
        except Exception:
            token = None
            base_repo = config.split(":")[0]
            url = ":".join(config.split(":")[1:])
            parts = base_repo.split("/")
            if len(parts) == 3:
                organisation = parts[0]
                project = parts[1]
                name = parts[2]
            elif len(parts) == 2:
                organisation = parts[0]
                project = ""
                name = parts[1]
            else:
                raise Exception(f"Configuration format is not ok: {config}")

        return cls(
            url=url,
            organisation=organisation,
            project=project,
            name=name,
            token=token,
        )
