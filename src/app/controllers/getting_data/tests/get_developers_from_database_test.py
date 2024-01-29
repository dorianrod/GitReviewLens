from src.app.controllers.getting_data.get_developers_from_database import (
    GetDevelopersController,
)
from src.domain.entities.developer import Developer
from src.infra.repositories.postgresql.developers import DeveloperDatabaseRepository


def test_get_developers(mock_logger, fixture_developer_dict):
    controller = GetDevelopersController(logger=mock_logger)
    db_repo = DeveloperDatabaseRepository(logger=mock_logger)

    developer = Developer.from_dict(fixture_developer_dict)
    db_repo.upsert(Developer.from_dict(fixture_developer_dict))

    assert controller.execute() == [developer]
