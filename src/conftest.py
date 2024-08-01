import asyncio
import os
from unittest.mock import Mock, patch

import pytest

from src.infra.database.postgresql.lock import EntityLockManager


@pytest.fixture
def mock_git_settings():
    from src.common.settings import __Settings

    class TestSettings(__Settings):
        app_name: str = "Pull requests"

        environment: str = "T"

        business_time_range: str = "09:00-18:00"

        db_port: int = 6432
        db_name: str = "test"
        db_host: str = "localhost"
        db_pass: str = "test"
        db_user: str = "test"

        db_schema: str = "test"

        init_sql: str = os.getenv("INIT_SQL_PATH", "../postgres/indicators.sql")

    settings = TestSettings()

    settings.git_branches = '[{"name":"master","repository":{"organisation":"orga","project":"project", "name": "Backend", "url": "orga/project/Backend:git@ssh.dev.azure.com:v3", "token": ""}},{"name":"master","repository":{"organisation":"orga", "project":"project", "name": "WebApp", "url": "orga/project/WebApp:git@ssh.dev.azure.com:v3", "token": ""}}]'

    return settings


@pytest.fixture
def fixture_feature_dict(fixture_developer_dict):
    return {
        "date": "2023-01-02T01:12:17",
        "git_repository": "orga/myrepo",
        "developer": fixture_developer_dict,
        "commit": "123",
        "count_deleted_lines": 1,
        "count_inserted_lines": 2,
        "dmm_unit_complexity": 0.5,
        "dmm_unit_interfacing": 0.6,
        "dmm_unit_size": 120,
        "modified_files": ["path/to/feature", "otherpath/to/anotherfeature"],
    }


@pytest.fixture
def fixture_developer_dict():
    return {"full_name": "Jean Dujardin", "email": "jean.dujardin@email.com"}


@pytest.fixture
def fixture_developer_2_dict():
    return {"full_name": "Thomas Dupont", "email": "thomas.dupont@email.com"}


@pytest.fixture
def fixture_developer_3_dict():
    return {"full_name": "Clark Kent", "email": "clark.kent@email.com"}


@pytest.fixture
def fixture_comment_dict(fixture_developer_dict):
    return {
        "pull_request_id": None,
        "content": "Please review this point",
        "developer": fixture_developer_dict,
        "creation_date": "2023-10-25T11:11:13",
    }


@pytest.fixture
def fixture_comment_2_dict(fixture_developer_2_dict):
    return {
        "content": "I am not sure to get it",
        "developer": fixture_developer_2_dict,
        "creation_date": "2023-10-26T11:10:13",
    }


@pytest.fixture
def fixture_pull_request_dict(
    fixture_developer_dict,
    fixture_developer_2_dict,
    fixture_comment_dict,
    fixture_comment_2_dict,
    fixture_developer_3_dict,
):
    return {
        "source_id": "10",
        "type": "feat",
        "git_repository": "orga/myrepo",
        "title": "feat 1",
        "approvers": [fixture_developer_dict, fixture_developer_2_dict],
        "comments": [fixture_comment_dict, fixture_comment_2_dict],
        "created_by": fixture_developer_3_dict,
        "creation_date": "2023-10-25T11:10:13",
        "completion_date": "2023-10-30T11:30:00",
        "source_branch": "feat/myfeat",
        "target_branch": "master",
        "previous_commit": "prev",
        "commit": "new",
    }


@pytest.fixture
def fixture_transcoder_dict():
    return {"name": 'type1', "values": {'a': '1', 'b': '2'}}


@pytest.fixture
def fixture_transcoder_2_dict():
    return {"name": 'other', "values": {'b': '1', 'c': '2'}}


@pytest.fixture(scope="function")
def mock_logger():
    from src.infra.monitoring.logger import LoggerDefault

    return Mock(spec=LoggerDefault)()


@pytest.fixture(autouse=True)
def patch_lock_manager():
    with patch(
        'src.infra.database.postgresql.lock.lock_manager',
        new=EntityLockManager(),
    ):
        yield


@pytest.fixture(scope='module')
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()
