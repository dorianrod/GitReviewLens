from src.app.controllers.extract_transform_load.load_features_from_repositories import (
    LoadFeaturesController,
)
from src.infra.monitoring.logger import LoggerDefault
from src.presentation.commands.base_command import Command

command = Command(LoadFeaturesController(logger=LoggerDefault()))
command.launch()
