import pytest

from src.infra.database.postgresql.database import create_grafana_indicators_in_database


@pytest.fixture(scope="function", autouse=True)
def mock_db(mocker, mock_git_settings):
    from src.infra.database.postgresql.database import drop_db, init_db

    mocker.patch(
        "src.infra.database.postgresql.database.settings",
        mock_git_settings,
    )
    drop_db()
    init_db(None)
    create_grafana_indicators_in_database()


@pytest.fixture(scope="function", autouse=True)
def clean_database(mock_db):
    from src.infra.database.postgresql.database import empty_db

    empty_db()
    yield


@pytest.fixture(scope="function")
def db_session():
    from src.infra.database.postgresql.database import get_db_session

    return get_db_session()
