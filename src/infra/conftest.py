import asyncio

import pytest

from src.infra.database.postgresql.database import create_grafana_indicators_in_database


@pytest.fixture(scope="function", autouse=True)
async def mock_db(mocker, mock_git_settings):
    from src.infra.database.postgresql.database import drop_db, init_db

    mocker.patch(
        "src.infra.database.postgresql.database.settings",
        mock_git_settings,
    )
    await drop_db()
    await init_db(None)
    await create_grafana_indicators_in_database()


@pytest.fixture(scope="function", autouse=True)
async def clean_database(mock_db):
    from src.infra.database.postgresql.database import empty_db

    await empty_db()
    yield


@pytest.fixture(scope="function")
def db_session():
    from src.infra.database.postgresql.database import get_db_session

    return get_db_session()


@pytest.fixture(scope='module')
def event_loop():
    # all tests in this directory will run in same loop
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()
