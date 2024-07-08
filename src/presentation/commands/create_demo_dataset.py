import asyncio

from src.app.controllers.extract_transform_load.anonymise_database_to_json import (
    AnonymizeDatabaseDataToJSONController,
)
from src.infra.monitoring.logger import LoggerDefault
from src.presentation.commands.base_command import Command

command = Command(
    AnonymizeDatabaseDataToJSONController(
        logger=LoggerDefault(), path="/demo", env_file_model="/.env.example"
    )
)
asyncio.run(command.launch(start_date="2022-01-01", end_date="2022-06-01"))
