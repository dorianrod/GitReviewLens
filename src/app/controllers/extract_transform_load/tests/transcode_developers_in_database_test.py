import os

import pytest

from src.app.controllers.extract_transform_load.transcode_developers_in_database import (
    TranscodeDevelopersInDatabaseController,
)
from src.domain.entities.developer import Developer
from src.domain.entities.transcoder import Transcoder
from src.infra.repositories.json.transcoders import TranscodersJsonRepository
from src.infra.repositories.postgresql.developers import DeveloperDatabaseRepository

current_file_path = os.path.abspath(__file__)
directory_of_file = os.path.dirname(current_file_path)
transco_path = os.path.join(directory_of_file, "temp", "transco.json")


def clean_path(path):
    if os.path.exists(path):
        os.remove(path)


@pytest.fixture(scope="function", autouse=True)
def clean_temp_files():
    clean_path(transco_path)


async def test_transcode_developers(mock_logger, fixture_developer_dict):
    db_repo = DeveloperDatabaseRepository(logger=mock_logger)
    await db_repo.upsert(Developer.from_dict(fixture_developer_dict))

    transco_repo = TranscodersJsonRepository(logger=mock_logger, path=transco_path)
    await transco_repo.upsert(
        Transcoder.from_dict(
            {
                "name": "developers_names_by_email",
                "values": {fixture_developer_dict["email"]: "toto"},
            }
        )
    )

    await TranscodeDevelopersInDatabaseController(
        logger=mock_logger, path=transco_path
    ).execute()

    developers = await db_repo.find_all()

    assert developers == [
        Developer.from_dict({**fixture_developer_dict, "full_name": "toto"})
    ]
