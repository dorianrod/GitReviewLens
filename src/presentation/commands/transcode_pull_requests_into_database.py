import asyncio

from src.app.controllers.extract_transform_load.transcode_pull_requests_in_database import (
    TranscodePullRequestsInDatabaseController,
)
from src.infra.monitoring.logger import LoggerDefault
from src.presentation.commands.base_command import Command

logger = LoggerDefault()

command = Command(TranscodePullRequestsInDatabaseController(logger=LoggerDefault()))
asyncio.run(command.launch())
