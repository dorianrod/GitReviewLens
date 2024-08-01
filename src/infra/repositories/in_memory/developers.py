from src.domain.entities.developer import Developer
from src.domain.repositories.developers import DeveloperRepository
from src.infra.repositories.in_memory.base import BaseInMemoryRepositoryMixin


class DevelopersInMemoryRepository(
    BaseInMemoryRepositoryMixin[Developer], DeveloperRepository
):
    pass
