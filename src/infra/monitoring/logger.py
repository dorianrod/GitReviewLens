import logging

from src.common.monitoring.logger import LoggerInterface
from src.common.settings import settings


class LoggerDefault(LoggerInterface):
    def __init__(self):
        logging.basicConfig(
            level=logging.DEBUG if settings.is_verbose else logging.INFO
        )

    def debug(self, message: str) -> None:
        logging.debug(message)

    def info(self, message: str) -> None:
        logging.info(message)

    def warning(self, message: str) -> None:
        logging.warning(message)

    def error(self, message: str) -> None:
        logging.error(message)

    def critical(self, message: str) -> None:
        logging.critical(message)

    def exception(self, message: str) -> None:
        logging.exception(message)


class MutedLogger(LoggerInterface):
    def debug(self, message: str) -> None:
        pass

    def info(self, message: str) -> None:
        pass

    def warning(self, message: str) -> None:
        pass

    def error(self, message: str) -> None:
        pass

    def critical(self, message: str) -> None:
        pass

    def exception(self, message: str) -> None:
        pass


logger = LoggerDefault()
