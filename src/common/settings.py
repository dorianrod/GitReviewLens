import json
import os

from pydantic_settings import BaseSettings

from ..domain.entities.branch import Branch


class __Settings(BaseSettings):
    app_name: str = "GitReviewers"

    environment: str = "P"

    calendar: str = os.getenv("CALENDAR", "FR")
    business_time_range: str = os.getenv("BUSINESS_TIMERANGE", "09:30-18:30")

    git_branches: str = os.getenv("GIT_BRANCHES", "")

    should_debugging: int = os.getenv("DEBUG", 0)  # type: ignore
    is_verbose: int = os.getenv("VERBOSE", 1)  # type: ignore

    db_port: int = os.getenv("DATABASE_PORT", 5432)  # type: ignore
    db_host: str = os.getenv("DATABASE_HOST", "")
    db_user: str = os.getenv("DATABASE_USER", "")
    db_pass: str = os.getenv("DATABASE_USER_PASSWORD", "")
    db_name: str = os.getenv("DATABASE_NAME", "")
    db_schema: str = os.getenv("DATABASE_SCHEMA", "public")

    init_sql: str = os.getenv("INIT_SQL", "/indicators.sql")

    def get_branches(self) -> list[Branch]:
        try:
            repositories_configuration = json.loads(self.git_branches)
        except Exception:
            raise Exception(
                f"Error parsing GIT_BRANCHES environment variable: {self.git_branches}"
            )

        repos = []
        for config in repositories_configuration:
            repos.append(Branch.parse(config))

        return repos

    @property
    def db_uri(self):
        return f"mysql+pymysql://{self.db_user}:{self.db_pass}@{self.db_host}:{self.db_port}/{self.db_name}"

    @property
    def version(self):
        return "1.0"


settings = __Settings()


def reload():
    global settings
    settings.git_branches = os.getenv("GIT_BRANCHES", "")
