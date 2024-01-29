from src.app.controllers.extract_transform_load.transcode_developers_in_database import (
    TranscodeDevelopersInDatabaseController,
)
from src.infra.monitoring.logger import LoggerDefault
from src.presentation.commands.base_command import Command

command = Command(TranscodeDevelopersInDatabaseController(logger=LoggerDefault()))
command.launch()
