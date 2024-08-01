import random
import string
from contextlib import asynccontextmanager

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker  # type: ignore
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from src.infra.database.postgresql.database import (
    get_db_session,
    get_db_uri,
    init_schema,
)
from src.infra.database.postgresql.models.factory import build_models


@pytest.fixture(scope="function", autouse=True)
async def db_schema():
    schema = "test_schema_" + ''.join(
        random.choices(string.ascii_lowercase + string.digits, k=8)
    )
    yield schema


@pytest.fixture(scope='function', autouse=True)
async def create_test_schema(mocker, db_schema, mock_git_settings, mock_get_db_session):
    # Each test run in a different schema
    schema_name = db_schema

    mock_git_settings.db_schema = schema_name
    mocker.patch(
        "src.infra.database.postgresql.database.settings",
        mock_git_settings,
    )

    model_load = build_models(db_schema)
    for key, Table in model_load.items():
        mocker.patch(
            f"src.infra.database.postgresql.models.models.{key}",
            Table,
        )

    mocker.patch(
        "src.infra.repositories.postgresql.developers.DeveloperDatabaseRepository.Model",
        new=model_load["Developer"],
    )
    mocker.patch(
        "src.infra.repositories.postgresql.comments.CommentsDatabaseRepository.Model",
        new=model_load["Comment"],
    )
    mocker.patch(
        "src.infra.repositories.postgresql.pull_requests.PullRequestsDatabaseRepository.Model",
        new=model_load["PullRequest"],
    )
    mocker.patch(
        "src.infra.repositories.postgresql.features.FeaturesDatabaseRepository.Model",
        new=model_load["Feature"],
    )

    async with get_db_session() as session:
        await session.execute(text(f"CREATE SCHEMA {schema_name}"))
        await session.commit()

    await init_schema(schema_name)
    yield schema_name

    # cleaning
    async with get_db_session() as session:
        try:
            await session.execute(text(f"DROP SCHEMA {schema_name}"))
            await session.commit()
        except Exception:
            pass


def get_async_engine():
    engine = create_async_engine(get_db_uri(), echo=False, pool_size=30, max_overflow=5)
    return engine


@pytest.fixture(scope='function', autouse=True)
async def mock_get_async_engine(mocker):
    mocker.patch(
        "src.infra.database.postgresql.database.get_async_engine",
        get_async_engine,
    )


@pytest.fixture(scope='function', autouse=True)
async def mock_get_db_session(mocker, event_loop, mock_get_async_engine):
    # A new session is needed for each test as tests are run in different schemas to really separate tests
    @asynccontextmanager
    async def get_db_session(schema=None):
        engine = create_async_engine(
            get_db_uri(),
            echo=False,
            pool_size=30,
            max_overflow=5,
            query_cache_size=0,
        )
        AsyncSessionLocal = async_sessionmaker(  # type: ignore
            bind=engine, class_=AsyncSession, expire_on_commit=False
        )
        async with AsyncSessionLocal() as session:
            await session.execute(text(f"SET search_path TO {schema}"))
            yield session

    mocker.patch(
        "src.infra.database.postgresql.database._get_db_session",
        get_db_session,
    )
