import os

import pytest

from src.app.controllers.database_dump_and_init.dump_database import (
    DumpDatabaseController,
)
from src.common.utils.file import delete_directory
from src.domain.entities.developer import Developer
from src.domain.entities.feature import Feature
from src.domain.entities.pull_request import PullRequest
from src.domain.entities.repository import Repository
from src.infra.repositories.json.developers import DevelopersJsonRepository
from src.infra.repositories.json.features import FeaturesJsonRepository
from src.infra.repositories.json.pull_requests import PullRequestsJsonRepository
from src.infra.repositories.postgresql.developers import DeveloperDatabaseRepository
from src.infra.repositories.postgresql.features import FeaturesDatabaseRepository
from src.infra.repositories.postgresql.pull_requests import (
    PullRequestsDatabaseRepository,
)

current_file_path = os.path.abspath(__file__)
directory_of_file = os.path.dirname(current_file_path)
path = os.path.join(directory_of_file, "temp")


@pytest.fixture(scope="function", autouse=True)
def mock_settings(mocker, mock_git_settings):
    mock_git_settings.git_branches = '[{"name":"master","repository":{"organisation":"orga","project":"", "name": "myrepo", "url": "", "token": ""}}]'

    mocker.patch(
        "src.app.controllers.database_dump_and_init.dump_database.settings",
        mock_git_settings,
    )


@pytest.fixture(scope="function", autouse=True)
def clean_temp_files():
    delete_directory(path)


async def test_dump_database(
    mock_logger, fixture_developer_dict, fixture_pull_request_dict, fixture_feature_dict
):
    git_repository = Repository.parse(fixture_feature_dict['git_repository'])

    dev_repo = DeveloperDatabaseRepository(logger=mock_logger)
    await dev_repo.upsert(Developer.from_dict(fixture_developer_dict))

    pr_repo = PullRequestsDatabaseRepository(
        logger=mock_logger, git_repository=git_repository
    )
    await pr_repo.upsert(
        PullRequest.from_dict(
            {**fixture_pull_request_dict, "git_repository": git_repository}
        )
    )

    feat_repo = FeaturesDatabaseRepository(
        logger=mock_logger, git_repository=git_repository
    )
    await feat_repo.upsert(
        Feature.from_dict({**fixture_feature_dict, "git_repository": git_repository})
    )

    controller = DumpDatabaseController(logger=mock_logger, path=path)
    await controller.execute()

    developers = await DevelopersJsonRepository(
        logger=mock_logger,
        path=f"{path}/developers.json",
    ).find_all()
    assert len(developers) == 3
    assert Developer.from_dict(fixture_developer_dict) in developers

    features = await FeaturesJsonRepository(
        logger=mock_logger,
        path=f"{path}/features.json",
        git_repository=git_repository,
    ).find_all()
    assert features == [Feature.from_dict(fixture_feature_dict)]

    pull_requets = await PullRequestsJsonRepository(
        logger=mock_logger,
        path=f"{path}/pull_requests.json",
        git_repository=git_repository,
    ).find_all()
    assert pull_requets == [PullRequest.from_dict(fixture_pull_request_dict)]


async def test_does_not_dump_other_repos(
    mock_logger, fixture_pull_request_dict, fixture_feature_dict
):
    git_repository = Repository.parse("orga/anotherrepo")

    pr_repo = PullRequestsDatabaseRepository(
        logger=mock_logger, git_repository=git_repository
    )
    await pr_repo.upsert(
        PullRequest.from_dict(
            {**fixture_pull_request_dict, "git_repository": git_repository}
        )
    )

    feat_repo = FeaturesDatabaseRepository(
        logger=mock_logger, git_repository=git_repository
    )
    await feat_repo.upsert(
        Feature.from_dict({**fixture_feature_dict, "git_repository": git_repository})
    )

    await DumpDatabaseController(logger=mock_logger, path=path).execute()

    features = await FeaturesJsonRepository(
        logger=mock_logger,
        path=f"{path}/features.json",
        git_repository=git_repository,
    ).find_all()
    assert features == []

    pull_requets = await PullRequestsJsonRepository(
        logger=mock_logger,
        path=f"{path}/pull_requests.json",
        git_repository=git_repository,
    ).find_all()
    assert pull_requets == []
