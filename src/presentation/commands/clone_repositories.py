from src.app.controllers.extract_transform_load.clone_repository import (
    CloneRepositoriesController,
)
from src.infra.monitoring.logger import LoggerDefault
from src.presentation.commands.base_command import Command

command = Command(CloneRepositoriesController(logger=LoggerDefault()))
command.launch()
