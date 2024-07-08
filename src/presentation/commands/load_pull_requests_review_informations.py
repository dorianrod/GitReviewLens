import asyncio

from src.app.controllers.extract_transform_load.load_pull_requests_from_remote_origins import (
    LoadPullRequestsFromRemoteOriginController,
)
from src.infra.monitoring.logger import LoggerDefault
from src.presentation.commands.base_command import Command

command = Command(LoadPullRequestsFromRemoteOriginController(logger=LoggerDefault()))
asyncio.run(command.launch())
