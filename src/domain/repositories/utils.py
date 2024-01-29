from typing import Any

from src.domain.entities.repository import Repository
from src.domain.exceptions import RepositoryIncompatibility


def raise_exception_if_repository_differs_from_entity(
    git_repository: Repository, entity: Any
):
    if str(entity.git_repository) != str(git_repository):
        raise RepositoryIncompatibility(
            f"Entity {str(entity)} has not the same git repository as the repository of the repository {git_repository}"
        )
