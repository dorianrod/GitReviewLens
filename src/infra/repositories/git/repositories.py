from dataclasses import dataclass

from git import RemoteProgress, Repo

#
from src.common.monitoring.logger import LoggerInterface
from src.common.utils.file import create_path_if_needed, delete_directory
from src.domain.repositories.repositories import GitRepoRepository


class ProgressLogger(RemoteProgress):
    def __init__(self, logger, name):
        super().__init__()
        self.name = name
        self.logger = logger

    def update(self, op_code, cur_count, max_count=None, message=''):
        progress_message = f'Cloning {self.name}: {str(round(100 * cur_count / max_count)) + "%" if cur_count else "?"}'
        self.logger.info(progress_message)


@dataclass
class GitRepoLocal(GitRepoRepository):
    name = "Cloning repository"

    logger: LoggerInterface
    path: str = "/repos"

    def clone(self, url, name):
        create_path_if_needed(self.path)
        delete_directory(f"{self.path}/{name}")

        progress_logger = ProgressLogger(self.logger, name=name)
        Repo.clone_from(
            url,
            f"{self.path}/{name}",
            allow_unsafe_protocols=True,
            allow_unsafe_options=True,
            multi_options=['--no-checkout'],
            progress=progress_logger,
        )

    def checkout(self, branch):
        try:
            repo = Repo(path=f"{self.path}/{branch.repository.name}")
            repo.git.checkout(branch.name)
            repo.git.reset("--hard", f"origin/{branch.name}")
        except Exception as e:
            self.logger.info(str(e))
            self.clone(branch.repository.url, branch.repository.name)
