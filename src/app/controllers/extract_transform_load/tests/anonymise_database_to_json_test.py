import os

import pytest

from src.app.controllers.extract_transform_load.anonymise_database_to_json import (
    AnonymizeDatabaseDataToJSONController,
)
from src.common.utils.file import delete_directory
from src.domain.entities.feature import Feature
from src.domain.entities.pull_request import PullRequest
from src.infra.repositories.json.features import FeaturesJsonRepository
from src.infra.repositories.json.pull_requests import PullRequestsJsonRepository
from src.infra.repositories.postgresql.features import FeaturesDatabaseRepository
from src.infra.repositories.postgresql.pull_requests import (
    PullRequestsDatabaseRepository,
)

current_file_path = os.path.abspath(__file__)
directory_of_file = os.path.dirname(current_file_path)
path = os.path.join(directory_of_file, "temp")

env_file_model = os.path.realpath(
    os.path.join(directory_of_file, "../../../../../.env.example")
)

git_repository = "orga/project/Backend"


@pytest.fixture(scope="function", autouse=True)
def mock_settings(mocker, mock_git_settings):
    mock_git_settings.git_branches = '[{"name":"master","repository":{"organisation":"orga","project":"project", "name": "Backend", "url": "orga/project/Backend:git@ssh.dev.azure.com:v3", "token": ""}}]'
    mocker.patch(
        "src.app.controllers.extract_transform_load.anonymise_database_to_json.settings",
        mock_git_settings,
    )


@pytest.fixture(scope="function", autouse=True)
def clean_temp_files():
    delete_directory(path)


@pytest.fixture(autouse=True)
async def dataset(mock_logger, fixture_pull_request_dict, fixture_feature_dict):
    db_pull_request_repo = PullRequestsDatabaseRepository(
        logger=mock_logger, git_repository=git_repository
    )
    await db_pull_request_repo.upsert(
        PullRequest.from_dict(
            {**fixture_pull_request_dict, "git_repository": git_repository}
        )
    )

    db_features_repo = FeaturesDatabaseRepository(
        logger=mock_logger, git_repository=git_repository
    )
    await db_features_repo.upsert(
        Feature.from_dict({**fixture_feature_dict, "git_repository": git_repository})
    )


async def test_anonymize_repositories(mock_logger):
    anonymized_git_repository = "demo/git/project_1"

    await AnonymizeDatabaseDataToJSONController(
        logger=mock_logger,
        path=path,
        env_file_model=env_file_model,
        git_repository=anonymized_git_repository,
    ).execute()

    json_repository_pull_request = PullRequestsJsonRepository(
        logger=mock_logger,
        git_repository=anonymized_git_repository,
        path=f"{path}/pull_requests.json",
    )

    json_repository_features = FeaturesJsonRepository(
        logger=mock_logger,
        git_repository=anonymized_git_repository,
        path=f"{path}/features.json",
    )

    pull_requests = await json_repository_pull_request.find_all()
    features = await json_repository_features.find_all()

    assert len(pull_requests) == 1
    assert len(features) == 1

    # Exhautive checks are done in the anonymize_dataset_test.py
    assert str(pull_requests[0].git_repository) != git_repository
    assert str(features[0].git_repository) != git_repository
