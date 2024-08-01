import os

import pytest

from src.app.controllers.database_dump_and_init.init_database import (
    InitDatabaseController,
)
from src.common.utils.file import delete_directory
from src.domain.entities.feature import Feature
from src.domain.entities.pull_request import PullRequest
from src.domain.entities.repository import Repository
from src.infra.repositories.postgresql.features import FeaturesDatabaseRepository
from src.infra.repositories.postgresql.pull_requests import (
    PullRequestsDatabaseRepository,
)

current_file_path = os.path.abspath(__file__)
directory_of_file = os.path.dirname(current_file_path)
path = os.path.join(directory_of_file, "temp")


@pytest.fixture(scope="function", autouse=True)
def mock_settings(mocker, mock_git_settings, db_schema):
    mock_git_settings.git_branches = '[{"name":"master","repository":{"organisation":"orga","project":"", "name": "myrepo", "url": "", "token": ""}}]'
    mock_git_settings.db_schema = db_schema

    mocker.patch(
        "src.app.controllers.database_dump_and_init.init_database.settings",
        mock_git_settings,
    )


@pytest.fixture(scope="function", autouse=True)
def clean_temp_files():
    delete_directory(path)


@pytest.fixture(scope="function")
async def create_remote_repositories(
    pull_request_repository,
    feature_repository,
    fixture_feature_dict,
    fixture_pull_request_dict,
    mock_logger,
):
    git_repository = Repository.parse(fixture_feature_dict['git_repository'])
    pull_request_repository.git_repository = git_repository
    feature_repository.git_repository = git_repository

    await pull_request_repository.upsert(
        PullRequest.from_dict(
            {**fixture_pull_request_dict, "git_repository": git_repository}
        )
    )
    await feature_repository.upsert(
        Feature.from_dict({**fixture_feature_dict, "git_repository": git_repository})
    )

    db_pull_request_repository = PullRequestsDatabaseRepository(
        logger=mock_logger, git_repository=git_repository
    )
    db_feature_repository = FeaturesDatabaseRepository(
        logger=mock_logger, git_repository=git_repository
    )

    return (
        feature_repository,
        pull_request_repository,
        db_feature_repository,
        db_pull_request_repository,
    )


async def test_init_database(
    mock_logger,
    get_temp_directory,
    create_remote_repositories,
):
    (
        feature_repository,
        pull_request_repository,
        db_feature_repository,
        db_pull_request_repository,
    ) = create_remote_repositories

    await InitDatabaseController(logger=mock_logger).execute(path=get_temp_directory)

    assert (
        await db_pull_request_repository.find_all()
        == await pull_request_repository.find_all()
    )
    assert await db_feature_repository.find_all() == await feature_repository.find_all()


async def test_does_not_load_features(
    mock_logger,
    get_temp_directory,
    create_remote_repositories,
):
    (
        _,
        pull_request_repository,
        db_feature_repository,
        db_pull_request_repository,
    ) = create_remote_repositories

    await InitDatabaseController(logger=mock_logger).execute(
        load_features=False, path=get_temp_directory
    )

    assert (
        await db_pull_request_repository.find_all()
        == await pull_request_repository.find_all()
    )
    assert await db_feature_repository.find_all() == []


async def test_does_not_load_pull_requests(
    mock_logger,
    get_temp_directory,
    create_remote_repositories,
):
    (
        feature_repository,
        _,
        db_feature_repository,
        db_pull_request_repository,
    ) = create_remote_repositories

    await InitDatabaseController(logger=mock_logger).execute(
        load_pull_requests=False, path=get_temp_directory
    )

    assert await db_pull_request_repository.find_all() == []
    assert await db_feature_repository.find_all() == await feature_repository.find_all()


async def test_does_not_drop_database(
    mock_logger,
    get_temp_directory,
    create_remote_repositories,
    fixture_pull_request_dict,
    fixture_feature_dict,
):
    (
        _feature_repository,
        _pull_request_repository,
        db_feature_repository,
        db_pull_request_repository,
    ) = create_remote_repositories

    pull_request = PullRequest.from_dict(
        {
            **fixture_pull_request_dict,
            "source_id": "1234",
            "git_repository": db_feature_repository.git_repository,
        }
    )
    await db_pull_request_repository.upsert(pull_request)

    feature = Feature.from_dict(
        {
            **fixture_feature_dict,
            "commit": "1234",
            "git_repository": db_feature_repository.git_repository,
        }
    )
    await db_feature_repository.upsert(feature)

    await InitDatabaseController(logger=mock_logger).execute(
        drop_db=False, path=get_temp_directory
    )

    db_pr = await db_pull_request_repository.find_all()
    db_feature = await db_feature_repository.find_all()

    assert len(db_pr) == 2
    assert len(db_feature) == 2

    assert feature in db_feature
    assert pull_request in db_pr

    for pr in db_pr:
        assert len(pr.comments) == 2
