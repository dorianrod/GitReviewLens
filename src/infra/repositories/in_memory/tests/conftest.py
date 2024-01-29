import pytest

from src.infra.repositories.in_memory.comments import CommentsInMemoryRepository
from src.infra.repositories.in_memory.developers import DevelopersInMemoryRepository
from src.infra.repositories.in_memory.features import FeaturesInMemoryRepository
from src.infra.repositories.in_memory.pull_requests import (
    PullRequestsInMemoryRepository,
)
from src.infra.repositories.in_memory.transcoders import TranscodersInMemoryRepository


@pytest.fixture(scope="function")
def transcoder_repository(mock_logger):
    return TranscodersInMemoryRepository(
        logger=mock_logger,
    )


@pytest.fixture(scope="function")
def pull_request_repository(mock_logger, fixture_pull_request_dict):
    return PullRequestsInMemoryRepository(
        logger=mock_logger,
        git_repository=fixture_pull_request_dict["git_repository"],
    )


@pytest.fixture(scope="function")
def pull_request_repository_2(mock_logger):
    return PullRequestsInMemoryRepository(
        logger=mock_logger,
        git_repository="orga/anotherrepo",
    )


@pytest.fixture(scope="function")
def developer_repository(mock_logger):
    return DevelopersInMemoryRepository(
        logger=mock_logger,
    )


@pytest.fixture(scope="function")
def comment_repository(mock_logger, fixture_pull_request_dict):
    return CommentsInMemoryRepository(
        logger=mock_logger,
        git_repository=fixture_pull_request_dict["git_repository"],
    )


@pytest.fixture(scope="function")
def comment_repository_2(mock_logger):
    return CommentsInMemoryRepository(
        logger=mock_logger,
        git_repository="orga/anotherrepo",
    )


@pytest.fixture(scope="function")
def feature_repository(mock_logger, fixture_feature_dict):
    return FeaturesInMemoryRepository(
        logger=mock_logger,
        git_repository=fixture_feature_dict["git_repository"],
    )


@pytest.fixture(scope="function")
def feature_repository_2(mock_logger):
    return FeaturesInMemoryRepository(
        logger=mock_logger,
        git_repository="orga/another_repo",
    )
