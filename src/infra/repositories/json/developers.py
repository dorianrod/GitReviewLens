from src.domain.entities.developer import Developer
from src.domain.repositories.developers import DeveloperRepository
from src.infra.repositories.json.base import BaseJsonRepositoryMixin


class DevelopersJsonRepository(BaseJsonRepositoryMixin[Developer], DeveloperRepository):
    entity_class = Developer  # type: ignore

    def __init__(self, path, *args, **kwargs):
        self.init(path)
        super().__init__(*args, **kwargs)
