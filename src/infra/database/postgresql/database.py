from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import create_database, database_exists, drop_database

from src.settings import settings

from .models.models import Base, Comment, Developer, Feature, PullRequest

__engine = None
__db_session = None


def create_grafana_indicators_in_database():
    with open(settings.init_sql, 'r') as f:
        sql_commands = f.read()

    if __db_session:
        __db_session.execute(text(sql_commands))
        __db_session.commit()


def get_db_session():
    global __db_session
    if not __db_session:
        init_db(None)

    return __db_session


def get_db_uri():
    return f"postgresql://{settings.db_user}:{settings.db_pass}@{settings.db_host}:{settings.db_port}/{settings.db_name}"


def init_db(app=None):
    global __engine
    global __db_session

    uri = get_db_uri()

    if not database_exists(uri):
        create_database(uri)

    connect_args = {"connect_timeout": 5}
    __engine = create_engine(uri, connect_args=connect_args)
    try:
        Base.metadata.create_all(__engine, checkfirst=True)
    except Exception as e:
        print(e)

    Session = sessionmaker(bind=__engine)
    __db_session = Session()

    if app:
        app.config["SQLALCHEMY_DATABASE_URI"] = uri
        app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


def empty_db():
    session = get_db_session()
    with session.begin():
        session.query(Feature).delete()
        session.query(Comment).delete()
        session.query(PullRequest).delete()
        session.query(Developer).delete()
    session.commit()


def drop_db():
    uri = get_db_uri()
    if database_exists(uri):
        drop_database(uri)
