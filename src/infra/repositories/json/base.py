import json
import os
from typing import Generic, Sequence, TypeVar

from src.common.utils.file import create_path_if_needed
from src.domain.entities.repository import Repository

_T = TypeVar("_T")


class BaseJsonRepositoryMixin(Generic[_T]):
    path: str
    entity_class: _T

    def init(self, path: str, *args, **kwargs):
        self.path = path

    def __dump_json(self, entities: Sequence[_T]):
        create_path_if_needed(self.path)
        with open(self.path, "w") as file:
            json_entities = [entity.to_dict() for entity in entities]  # type: ignore
            json.dump(json_entities, file, indent=4)

    def upsert(self, entity: _T, options: dict | None = None):
        super().upsert(entity, options)  # type: ignore

        entities: list[_T] = self.find_all(options)  # type: ignore

        i = 0
        found = False
        for old_entity in entities:
            if old_entity.id == entity.id:  # type: ignore
                found = True
                entities[i] = entity
                break
            i += 1

        if not found:
            entities.append(entity)

        self.__dump_json(entities)

    def upsert_all(self, entities: Sequence[_T], options=None):
        self.__dump_json(entities)

    def find_all(self, options=None) -> Sequence[_T]:
        if not os.path.isfile(self.path):
            return []

        try:
            with open(self.path, "r") as file:
                data = json.load(file)
                return [self.entity_class.from_dict(entity) for entity in data]  # type: ignore
        except Exception:
            return []


class BaseRepoJsonRepositoryMixin(BaseJsonRepositoryMixin[_T]):
    def init(self, path, git_repository, *args, **kwargs):
        super().init(path)  # type: ignore

        git_repository = Repository.parse(git_repository)
        file = str(git_repository).replace("/", "_")  # type: ignore
        self.path = self.path.replace(".json", f"_{file}.json")
