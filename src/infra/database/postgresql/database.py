from contextlib import asynccontextmanager

from sqlalchemy import create_engine, delete, text
from sqlalchemy.ext.asyncio import async_sessionmaker  # type: ignore
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import create_database, database_exists, drop_database

from src.common.settings import settings
from src.infra.database.postgresql.models.factory import build_models

from .models.models import Comment, Developer, Feature, PullRequest

__engine = None
AsyncSessionLocal = None


def create_sync_session():
    Session = sessionmaker(
        bind=create_engine(get_db_uri(False), connect_args={"connect_timeout": 5}),
        expire_on_commit=True,
    )
    session = Session()
    return session


async def create_grafana_indicators_in_database(schema):
    with open(settings.init_sql, 'r') as f:
        sql_commands = f.read()
        sql_commands = sql_commands.replace("public.", schema + ".")
    session = create_sync_session()
    with session.begin():
        session.execute(text(f"SET search_path TO {schema}"))
        session.execute(text(sql_commands))
    session.commit()


@asynccontextmanager
async def _get_db_session():
    global AsyncSessionLocal
    if not AsyncSessionLocal:
        AsyncSessionLocal = async_sessionmaker(
            bind=get_async_engine(), class_=AsyncSession, expire_on_commit=False
        )

    assert AsyncSessionLocal is not None
    async with AsyncSessionLocal() as session:
        yield session


@asynccontextmanager
async def _start_transaction():
    async with _get_db_session() as session:
        if session.in_transaction():
            async with session.begin_nested():
                yield session
        else:
            async with session.begin():
                yield session


@asynccontextmanager
async def start_transaction():
    async with _start_transaction() as session:
        yield session


@asynccontextmanager
async def get_db_session():
    async with _get_db_session() as session:
        yield session


def get_async_engine():
    global __engine
    if not __engine:
        __engine = create_async_engine(
            get_db_uri(), echo=False, pool_size=30, max_overflow=5
        )

    return __engine


def get_db_uri(asyncpg=True):
    asyncpg_suffix = "+asyncpg" if asyncpg else ""
    return f"postgresql{asyncpg_suffix}://{settings.db_user}:{settings.db_pass}@{settings.db_host}:{settings.db_port}/{settings.db_name}"


async def create_schema(schema):
    async with get_db_session() as session:
        await session.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema}"))
        await session.commit()


async def init_schema(schema):
    async with get_async_engine().begin() as conn:
        Base = build_models(schema)["Base"]
        await create_schema(schema)
        await conn.run_sync(Base.metadata.create_all)
        await create_grafana_indicators_in_database(schema)


async def init_db(schema=None):
    sync_uri = get_db_uri(False)
    if not database_exists(sync_uri):
        create_database(sync_uri)
        await init_schema(schema)


async def empty_db():
    async with get_db_session() as session:
        async with session.begin():
            for model in [Feature, Comment, PullRequest, Developer]:
                try:
                    await session.execute(delete(model))
                except Exception:
                    pass
        await session.commit()


async def drop_db():
    uri = get_db_uri(False)
    if database_exists(uri):
        drop_database(uri)
