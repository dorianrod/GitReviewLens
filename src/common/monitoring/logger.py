from abc import ABC, abstractmethod


class LoggerInterface(ABC):
    """LoggerInterface class provides an interface for logging."""

    @abstractmethod
    def debug(self, message: str) -> None:
        """Log debug message.
        :param message: Message to log.
        """

    @abstractmethod
    def info(self, message: str) -> None:
        """Log info message.
        :param message: Message to log.
        """

    @abstractmethod
    def warning(self, message: str) -> None:
        """Log warning message.
        :param message: Message to log.
        """

    @abstractmethod
    def error(self, message: str) -> None:
        """Log error message.
        :param message: Message to log.
        """

    @abstractmethod
    def critical(self, message: str) -> None:
        """Log critical message.
        :param message: Message to log.
        """

    @abstractmethod
    def exception(self, message: str) -> None:
        """Log exception message with exception info.
        :param message: Message to log.
        """
