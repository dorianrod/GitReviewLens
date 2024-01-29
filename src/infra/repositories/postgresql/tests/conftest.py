import pytest

from src.infra.repositories.postgresql.comments import CommentsDatabaseRepository
from src.infra.repositories.postgresql.developers import DeveloperDatabaseRepository
from src.infra.repositories.postgresql.features import FeaturesDatabaseRepository
from src.infra.repositories.postgresql.pull_requests import (
    PullRequestsDatabaseRepository,
)


@pytest.fixture(scope="function")
def pull_request_repository(mock_logger, fixture_pull_request_dict):
    return PullRequestsDatabaseRepository(
        logger=mock_logger,
        git_repository=fixture_pull_request_dict["git_repository"],
    )


@pytest.fixture(scope="function")
def pull_request_repository_2(mock_logger):
    return PullRequestsDatabaseRepository(
        logger=mock_logger,
        git_repository="orga/anotherrepo",
    )


@pytest.fixture(scope="function")
def developer_repository(mock_logger):
    return DeveloperDatabaseRepository(
        logger=mock_logger,
    )


@pytest.fixture(scope="function")
def comment_repository(mock_logger, fixture_pull_request_dict):
    return CommentsDatabaseRepository(
        logger=mock_logger,
        git_repository=fixture_pull_request_dict["git_repository"],
    )


@pytest.fixture(scope="function")
def comment_repository_2(mock_logger):
    return CommentsDatabaseRepository(
        logger=mock_logger,
        git_repository="orga/anotherrepo",
    )


@pytest.fixture(scope="function")
def feature_repository(mock_logger, fixture_feature_dict):
    return FeaturesDatabaseRepository(
        logger=mock_logger,
        git_repository=fixture_feature_dict["git_repository"],
    )


@pytest.fixture(scope="function")
def feature_repository_2(mock_logger):
    return FeaturesDatabaseRepository(
        logger=mock_logger,
        git_repository="orga/another_repo",
    )
