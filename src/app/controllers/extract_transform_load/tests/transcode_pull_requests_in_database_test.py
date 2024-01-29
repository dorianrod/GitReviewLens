import os

import pytest

from src.app.controllers.extract_transform_load.transcode_pull_requests_in_database import (
    TranscodePullRequestsInDatabaseController,
)
from src.domain.entities.pull_request import PullRequest
from src.domain.entities.transcoder import Transcoder
from src.infra.repositories.json.transcoders import TranscodersJsonRepository
from src.infra.repositories.postgresql.pull_requests import (
    PullRequestsDatabaseRepository,
)

current_file_path = os.path.abspath(__file__)
directory_of_file = os.path.dirname(current_file_path)
transco_path = os.path.join(directory_of_file, "temp", "transco.json")


def clean_path(path):
    if os.path.exists(path):
        os.remove(path)


@pytest.fixture(scope="function", autouse=True)
def mock_settings(mocker, mock_git_settings):
    mock_git_settings.git_branches = '[{"name":"master","repository":{"organisation":"orga","project":"project", "name": "Backend", "url": "orga/project/Backend:git@ssh.dev.azure.com:v3", "token": ""}}]'

    mocker.patch(
        "src.app.controllers.extract_transform_load.transcode_pull_requests_in_database.settings",
        mock_git_settings,
    )


@pytest.fixture(scope="function", autouse=True)
def clean_temp_files():
    clean_path(transco_path)


def test_transcode_pull_requests(mock_logger, fixture_pull_request_dict):
    db_repo = PullRequestsDatabaseRepository(
        logger=mock_logger, git_repository="orga/project/Backend"
    )
    db_repo.upsert(
        PullRequest.from_dict(
            {**fixture_pull_request_dict, "git_repository": "orga/project/Backend"}
        )
    )

    transco_repo = TranscodersJsonRepository(logger=mock_logger, path=transco_path)
    transco_repo.upsert(
        Transcoder.from_dict(
            {
                "name": "pull_requests_type",
                "values": {"feat": "feature"},
            }
        )
    )

    TranscodePullRequestsInDatabaseController(
        logger=mock_logger, path=transco_path
    ).execute()

    pull_requests = db_repo.find_all()

    assert pull_requests == [
        PullRequest.from_dict(
            {
                **fixture_pull_request_dict,
                "git_repository": "orga/project/Backend",
                "type": "feature",
            }
        )
    ]


def test_does_not_transcode_pull_requests(mock_logger, fixture_pull_request_dict):
    db_repo_2 = PullRequestsDatabaseRepository(
        logger=mock_logger,
        git_repository="orga/myrepo",
    )
    db_repo_2.upsert(PullRequest.from_dict(fixture_pull_request_dict))

    transco_repo = TranscodersJsonRepository(logger=mock_logger, path=transco_path)
    transco_repo.upsert(
        Transcoder.from_dict(
            {
                "name": "pull_requests_type",
                "values": {"feat": "feature"},
            }
        )
    )

    TranscodePullRequestsInDatabaseController(
        logger=mock_logger, path=transco_path
    ).execute()

    pull_requests = db_repo_2.find_all()

    assert pull_requests == [PullRequest.from_dict(fixture_pull_request_dict)]
