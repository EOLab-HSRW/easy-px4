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


class BaseFolderStructure(ABC):
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


class SITLFolderStructure(BaseFolderStructure):
    def get_rules(self) -> list[FileRule]:
        return [
            FileRule("info_file", "info.toml"),
            FileRule("params_file", "params.airframe"),
            FileRule("modules_file", "sitl.modules"),
        ]



class FirmwareFolderStructure(BaseFolderStructure):
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
    def __init__(self, folder: Union[str, Path], build_type: str):

        self.folder = valid_dir_path(folder)

        self.build_type = build_type

        self.__structure = self.__validate_structure()

        for rule in self.__structure.get_rules():
            setattr(self, rule.prop_name, rule.file_name)

        self.info = load_info(self.folder / self.__structure.info_file)

    def __validate_structure(self):
        structure = None
        if self.build_type == "sitl":
            structure = SITLFolderStructure()
        elif self.build_type == "firmware":
            structure = FirmwareFolderStructure()
        else:
            raise ValueError(f"Unknown build type: {self.build_type}")

        structure.validate(self.folder)
        return structure


def load_directory(path: Union[str, Path]) -> Directory:

    return Directory(path, build_type="firmware")
