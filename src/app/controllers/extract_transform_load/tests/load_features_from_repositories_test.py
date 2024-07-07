import os
import zipfile
from unittest.mock import patch

import pytest

from src.app.controllers.extract_transform_load.load_features_from_repositories import (
    GitRepoLocal,
    LoadFeaturesController,
)
from src.domain.entities.feature import Feature
from src.infra.repositories.postgresql.features import FeaturesDatabaseRepository


async def test_extract_features_from_local_repo(mock_logger, mock_settings):
    with patch.object(
        GitRepoLocal,
        'checkout',
        return_value=[],
    ):
        controller = LoadFeaturesController(logger=mock_logger, path=repo_path)
        await controller.execute()

        db_features_repository = FeaturesDatabaseRepository(
            logger=mock_logger,
            git_repository=mock_settings.get_branches()[0].repository,
        )

        features_in_db = await db_features_repository.find_all()

        assert [feature.to_dict() for feature in features_in_db] == expected_result


async def test_works_when_already_loaded_features(mock_logger, mock_settings):
    with patch.object(
        GitRepoLocal,
        'checkout',
        return_value=[],
    ):
        db_features_repository = FeaturesDatabaseRepository(
            logger=mock_logger,
            git_repository=mock_settings.get_branches()[0].repository,
        )

        feature_1 = Feature.from_dict(
            {
                "count_deleted_lines": 0,
                "count_inserted_lines": 1,
                "dmm_unit_complexity": 0.0,
                "dmm_unit_interfacing": 0.0,
                "dmm_unit_size": 0.0,
                "modified_files": ["__init..py"],
                "developer": {
                    "full_name": "Newname",
                    "email": "new@email",
                    "id": "new@email",
                },
                "commit": "b2ea326a578d8e2aecf72ece9a0b14ec898d9cf8",
                "date": "2023-12-23T09:29:45Z",
                "git_repository": "orga/myrepo",
                "count_modified_lines": 1,
                "count_modified_files": 1,
            }
        )

        feature_2 = Feature.from_dict(
            {
                "count_deleted_lines": 0,
                "count_inserted_lines": 1,
                "dmm_unit_complexity": 0.0,
                "dmm_unit_interfacing": 0.0,
                "dmm_unit_size": 0.0,
                "modified_files": ["add_file.py"],
                "developer": {
                    "full_name": "Newname",
                    "email": "new@email",
                    "id": "new@email",
                },
                "commit": "97b49bad5cfc535d1d5d85a301d218faf7570e37",
                "date": "2023-12-23T09:30:08Z",
                "git_repository": "orga/myrepo",
                "count_modified_lines": 1,
                "count_modified_files": 1,
            }
        )

        await db_features_repository.upsert_all([feature_1, feature_2])

        controller = LoadFeaturesController(logger=mock_logger, path=repo_path)
        await controller.execute()

        features_in_db = await db_features_repository.find_all()
        assert [feature.to_dict() for feature in features_in_db] == expected_result


current_file_path = os.path.abspath(__file__)
directory_of_file = os.path.dirname(current_file_path)
fixture_path = os.path.join(directory_of_file, "fixture")
repo_path = os.path.join(fixture_path, "git", "repos")
unzip_git_path = os.path.join(repo_path, "myrepo")


@pytest.fixture(scope="module", autouse=True)
def unzip_fixture():
    git_file = os.path.join(fixture_path, "git.zip")

    def unzip_file(file_path, destination_path):
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            zip_ref.extractall(destination_path)

    unzip_file(git_file, unzip_git_path)


@pytest.fixture(scope="function", autouse=True)
def mock_settings(mocker, mock_git_settings):
    mock_git_settings.git_branches = '[{"name":"main","repository":{"organisation":"orga","project":"", "name": "myrepo", "url": "", "token": ""}}]'

    mocker.patch(
        "src.app.controllers.extract_transform_load.load_features_from_repositories.settings",
        mock_git_settings,
    )

    return mock_git_settings


expected_result = [
    {
        "count_deleted_lines": 0,
        "count_inserted_lines": 1,
        "dmm_unit_complexity": 0.0,
        "dmm_unit_interfacing": 0.0,
        "dmm_unit_size": 0.0,
        "modified_files": ["__init..py"],
        "developer": {
            "full_name": "Newname",
            "email": "new@email",
            "id": "new@email",
        },
        "commit": "b2ea326a578d8e2aecf72ece9a0b14ec898d9cf8",
        "date": "2023-12-23T09:29:45Z",
        "git_repository": "orga/myrepo",
        "count_modified_lines": 1,
        "count_modified_files": 1,
    },
    {
        "count_deleted_lines": 0,
        "count_inserted_lines": 1,
        "dmm_unit_complexity": 0.0,
        "dmm_unit_interfacing": 0.0,
        "dmm_unit_size": 0.0,
        "modified_files": ["add_file.py"],
        "developer": {
            "full_name": "Newname",
            "email": "new@email",
            "id": "new@email",
        },
        "commit": "97b49bad5cfc535d1d5d85a301d218faf7570e37",
        "date": "2023-12-23T09:30:08Z",
        "git_repository": "orga/myrepo",
        "count_modified_lines": 1,
        "count_modified_files": 1,
    },
    {
        "count_deleted_lines": 1,
        "count_inserted_lines": 1,
        "dmm_unit_complexity": 0.0,
        "dmm_unit_interfacing": 0.0,
        "dmm_unit_size": 0.0,
        "modified_files": ["add_file.py"],
        "developer": {
            "full_name": "Newname",
            "email": "new@email",
            "id": "new@email",
        },
        "commit": "4dbd8e276a5f0f55abf40c2eba66176962420f69",
        "date": "2023-12-23T09:30:19Z",
        "git_repository": "orga/myrepo",
        "count_modified_lines": 2,
        "count_modified_files": 1,
    },
    {
        "count_deleted_lines": 1,
        "count_inserted_lines": 0,
        "dmm_unit_complexity": 0.0,
        "dmm_unit_interfacing": 0.0,
        "dmm_unit_size": 0.0,
        "modified_files": ["add_file.py"],
        "developer": {
            "full_name": "Newname",
            "email": "new@email",
            "id": "new@email",
        },
        "commit": "c423e98a1fd069a90fd45e957868b7d0fbe242ca",
        "date": "2023-12-23T09:30:29Z",
        "git_repository": "orga/myrepo",
        "count_modified_lines": 1,
        "count_modified_files": 1,
    },
]
