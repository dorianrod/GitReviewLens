from contextlib import asynccontextmanager

from sqlalchemy import create_engine, delete, text
from sqlalchemy.ext.asyncio import async_sessionmaker  # type: ignore
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import create_database, database_exists, drop_database

from src.settings import settings

from .models.models import Base, Comment, Developer, Feature, PullRequest

__engine = None
AsyncSessionLocal = None


def create_sync_session():
    Session = sessionmaker(
        bind=create_engine(get_db_uri(False), connect_args={"connect_timeout": 5}),
        expire_on_commit=True,
    )
    session = Session()
    return session


async def create_grafana_indicators_in_database():
    with open(settings.init_sql, 'r') as f:
        sql_commands = f.read()
    session = create_sync_session()
    with session.begin():
        session.execute(text(sql_commands))
    session.commit()


@asynccontextmanager
async def get_db_session():
    global AsyncSessionLocal
    if not AsyncSessionLocal:
        AsyncSessionLocal = async_sessionmaker(  # type: ignore
            bind=get_async_engine(), class_=AsyncSession, expire_on_commit=False
        )

    assert AsyncSessionLocal is not None
    async with AsyncSessionLocal() as session:
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


async def init_db(app=None):
    sync_uri = get_db_uri(False)
    if not database_exists(sync_uri):
        create_database(sync_uri)
        async with get_async_engine().begin() as conn:
            await conn.run_sync(Base.metadata.create_all)


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
