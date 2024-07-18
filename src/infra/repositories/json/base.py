import json
import os
from typing import Generic, Sequence, TypeVar

from src.common.utils.file import create_path_if_needed
from src.domain.entities.common import BaseEntity
from src.domain.entities.repository import Repository

_T = TypeVar("_T", bound=BaseEntity)


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

    async def upsert(self, entity: _T, options: dict | None = None):
        await self.upsert_all([entity], options)

    async def upsert_all(self, entities: Sequence[_T], options=None):
        current_entities: list[_T] = await self.find_all(options)  # type: ignore

        entities_to_update_by_id = {entity.id: entity for entity in entities}
        ids_to_create = set(entities_to_update_by_id.keys())

        i = 0
        for old_entity in current_entities:
            if entities_to_update_by_id.get(old_entity.id):  # type: ignore
                ids_to_create.remove(old_entity.id)
                current_entities[i] = entities_to_update_by_id[old_entity.id]
                break
            i += 1

        for id in ids_to_create:
            current_entities.append(entities_to_update_by_id[id])

        self.__dump_json(current_entities)

    async def find_all(self, options=None) -> list[_T]:
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
