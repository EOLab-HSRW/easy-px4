from abc import ABC, abstractmethod
from argparse import ArgumentParser, Namespace
from ..logger import get_logger

class Command(ABC):

    # This refers to the way in which this command is exposed to the cli
    cmd_name: str = "command"  # Must be overridden with the name of the cli command

    def __init__(self) -> None:
        if not self.cmd_name:
            raise NotImplementedError(
                f"{self.__class__.__name__} must define class attribute `cli_cmd`"
            )
        self.logger = get_logger(self.cmd_name)

    @abstractmethod
    def add_arguments(self, parser: ArgumentParser):
        """
        Registration of arguments for the parser.
        """
        pass

    @abstractmethod
    def execute(self, args: Namespace):
        """
        Action to perform while calling the command
        """
        pass

    def cleanup(self):
        pass

    def preparation(self):
        pass

    def __enter__(self):
        self.preparation()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()

