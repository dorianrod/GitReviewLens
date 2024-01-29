import os

import pytest

from src.infra.repositories.json.developers import DevelopersJsonRepository
from src.infra.repositories.json.features import FeaturesJsonRepository
from src.infra.repositories.json.pull_requests import PullRequestsJsonRepository
from src.infra.repositories.json.transcoders import TranscodersJsonRepository

current_file_path = os.path.abspath(__file__)
directory_of_file = os.path.dirname(current_file_path)
temp_directory = os.path.join(directory_of_file, "temp")

dev_path = os.path.join(temp_directory, "developers.json")
comment_path = os.path.join(temp_directory, "comments.json")
pull_requests_path = os.path.join(temp_directory, "pull_requests.json")
features_path = os.path.join(temp_directory, "features.json")
transcoder_path = os.path.join(temp_directory, "transcoders.json")


@pytest.fixture
def get_temp_directory():
    return temp_directory


def clean_path(repository):
    if os.path.exists(repository.path):
        os.remove(repository.path)


@pytest.fixture(scope="function")
def transcoder_repository(mock_logger):
    repo = TranscodersJsonRepository(logger=mock_logger, path=transcoder_path)
    clean_path(repo)
    return repo


@pytest.fixture(scope="function")
def pull_request_repository(mock_logger, fixture_pull_request_dict):
    repo = PullRequestsJsonRepository(
        logger=mock_logger,
        git_repository=fixture_pull_request_dict["git_repository"],
        path=pull_requests_path,
    )
    clean_path(repo)
    return repo


@pytest.fixture(scope="function")
def pull_request_repository_2(mock_logger):
    repo = PullRequestsJsonRepository(
        logger=mock_logger, git_repository="orga/anotherrepo", path=pull_requests_path
    )
    clean_path(repo)
    return repo


@pytest.fixture(scope="function")
def developer_repository(mock_logger):
    repo = DevelopersJsonRepository(logger=mock_logger, path=dev_path)
    clean_path(repo)
    return repo


@pytest.fixture
def comment_repository():
    return None


@pytest.fixture
def comment_repository_2():
    return None


@pytest.fixture(scope="function")
def feature_repository(mock_logger, fixture_feature_dict):
    repo = FeaturesJsonRepository(
        logger=mock_logger,
        git_repository=fixture_feature_dict["git_repository"],
        path=features_path,
    )
    clean_path(repo)
    return repo


@pytest.fixture(scope="function")
def feature_repository_2(mock_logger):
    repo = FeaturesJsonRepository(
        logger=mock_logger, git_repository="orga/another_repo", path=features_path
    )
    clean_path(repo)
    return repo
