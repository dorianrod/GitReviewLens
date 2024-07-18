from dataclasses import dataclass
from datetime import datetime

from src.common.utils.date import format_to_iso, parse_date
from src.common.utils.json import recursive_asdict
from src.domain.entities.common import BaseEntity
from src.domain.entities.developer import Developer
from src.domain.entities.repository import Repository


@dataclass
class Feature(BaseEntity):
    count_deleted_lines: int
    count_inserted_lines: int
    dmm_unit_complexity: float
    dmm_unit_interfacing: float
    dmm_unit_size: float
    modified_files: list[str]
    developer: Developer
    commit: str
    date: datetime
    git_repository: Repository

    @property
    def id(self):
        return str(hash((self.commit, self.git_repository.path)))

    @property
    def count_modified_lines(self):
        return self.count_deleted_lines + self.count_inserted_lines

    @property
    def count_modified_files(self):
        return len(self.modified_files)

    @classmethod
    def from_dict(cls, data):
        developer = (
            data.get("developer")
            if isinstance(data.get("developer"), Developer)
            else Developer.from_dict(data.get("developer"))
        )

        return cls(
            git_repository=Repository.parse(data.get("git_repository")),
            count_deleted_lines=int(data.get("count_deleted_lines", 0)),
            count_inserted_lines=int(data.get("count_inserted_lines", 0)),
            dmm_unit_complexity=float(data.get("dmm_unit_complexity", 0) or 0),
            dmm_unit_interfacing=float(data.get("dmm_unit_interfacing", 0) or 0),
            dmm_unit_size=float(data.get("dmm_unit_size", 0) or 0),
            modified_files=list(data.get("modified_files", [])).copy(),
            date=parse_date(data.get("date", [])),
            commit=data.get("commit"),
            developer=developer,
        )

    def to_dict(self):
        return {
            **recursive_asdict(self),
            "git_repository": self.git_repository.path,
            "date": format_to_iso(self.date),
            "count_modified_lines": self.count_modified_lines,
            "count_modified_files": self.count_modified_files,
        }

    def __repr__(self):
        return f"<Feature {self.id} - {self.git_repository}>"

    @staticmethod
    def get_developers_from_list(features: list['Feature']) -> list[Developer]:
        developers_set: set[Developer] = set()
        for feature in features:
            developers_set.add(feature.developer)
        return list(developers_set)
