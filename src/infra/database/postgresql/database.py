from contextlib import asynccontextmanager

from sqlalchemy import create_engine, delete, text
from sqlalchemy.ext.asyncio import async_sessionmaker  # type: ignore
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import create_database, database_exists, drop_database

from src.settings import settings

from .models.models import Base, Comment, Developer, Feature, PullRequest

__engine = None
__db_session = None
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
        await init_db(None)

    assert AsyncSessionLocal is not None
    async with AsyncSessionLocal() as session:
        yield session


def get_engine():
    global __engine
    return __engine


def get_db_uri(asyncpg=True):
    asyncpg_suffix = "+asyncpg" if asyncpg else ""
    return f"postgresql{asyncpg_suffix}://{settings.db_user}:{settings.db_pass}@{settings.db_host}:{settings.db_port}/{settings.db_name}"


async def init_db(app=None):
    global __engine, __db_session, AsyncSessionLocal

    uri = get_db_uri()
    sync_uri = get_db_uri(False)
    if not database_exists(sync_uri):
        create_database(sync_uri)

    __engine = create_async_engine(uri, echo=False, pool_size=30, max_overflow=5)
    try:
        async with __engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    except Exception as e:
        print(e)

    AsyncSessionLocal = async_sessionmaker(  # type: ignore
        bind=__engine, class_=AsyncSession, expire_on_commit=False
    )
    __db_session = AsyncSessionLocal()

    if app:
        app.config["SQLALCHEMY_DATABASE_URI"] = uri
        app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


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
