from src.app.controllers.extract_transform_load.check_settings import CheckSettings
from src.infra.monitoring.logger import LoggerDefault
from src.presentation.commands.base_command import Command

command = Command(CheckSettings(logger=LoggerDefault()))
command.launch()
