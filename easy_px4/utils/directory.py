from abc import ABC, abstractmethod
from pathlib import Path
from dataclasses import dataclass
from typing import Union
from .info import load_info

@dataclass(frozen=True)
class FileRule:
    prop_name: str
    file_name: str
    required: bool = True


class BaseDirectoryStructure(ABC):
    def __init__(self):
        self.rules = self.get_rules()

        for rule in self.rules:
            setattr(self, rule.prop_name, rule.file_name)

    @abstractmethod
    def get_rules(self) -> list[FileRule]:
        """Return the list of file rules required for this folder structure."""
        pass

    def validate(self, folder: Path) -> None:
        missing = [
            rule.file_name
            for rule in self.rules
            if rule.required and not (folder / rule.file_name).is_file()
        ]
        if missing:
            raise FileNotFoundError(f"Missing required files: {', '.join(missing)}")


class SITLDirectoryStructure(BaseDirectoryStructure):
    def get_rules(self) -> list[FileRule]:
        return [
            FileRule("info_file", "info.toml"),
            FileRule("params_file", "params.airframe"),
            FileRule("modules_file", "sitl.modules"),
        ]



class FirmwareDirectoryStructure(BaseDirectoryStructure):
    def get_rules(self) -> list[FileRule]:
        return [
            FileRule("info_file", "info.toml"),
            FileRule("params_file", "params.airframe"),
            FileRule("modules_file", "board.modules"),
        ]

def valid_dir_path(path: Union[str, Path]) -> Path:

    directory = None

    if isinstance(path, str):
        directory = Path(path)
    elif isinstance(path, Path):
        directory = path
    else:
        raise TypeError(f"path must be str or Path, got {type(path).__name__}")

    if not directory.exists():
        raise FileNotFoundError(f"Path does not exist: {directory}")
    if not directory.is_dir():
        raise NotADirectoryError(f"Expected a directory but got: {directory}")

    return directory

class Directory:
    def __init__(self, path: Union[str, Path], dir_type: str):

        self.directory = valid_dir_path(path)

        self.dir_type = dir_type

        self.__structure = self.__validate_structure()

        for rule in self.__structure.get_rules():
            setattr(self, rule.prop_name, rule.file_name)

        self.info = load_info(self.directory / self.__structure.info_file)

    def __validate_structure(self):
        structure = None
        if self.dir_type == "sitl":
            structure = SITLDirectoryStructure()
        elif self.dir_type == "firmware":
            structure = FirmwareDirectoryStructure()
        else:
            raise ValueError(f"Unknown build type: {self.dir_type}")

        structure.validate(self.directory)
        return structure


def load_directory(path: Union[str, Path], dir_type: str) -> Directory:

    return Directory(path, dir_type)
