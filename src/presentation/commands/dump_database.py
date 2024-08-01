import asyncio

from src.app.controllers.database_dump_and_init.dump_database import (
    DumpDatabaseController,
)
from src.infra.monitoring.logger import LoggerDefault
from src.presentation.commands.base_command import Command

command = Command(DumpDatabaseController(logger=LoggerDefault()))
asyncio.run(command.launch())
