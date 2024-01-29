from dataclasses import dataclass

from src.app.controllers.base_controller import BaseController


@dataclass
class Command:
    use_case: BaseController

    def launch(self, *args, **kwargs):
        self.use_case.execute(*args, **kwargs)
