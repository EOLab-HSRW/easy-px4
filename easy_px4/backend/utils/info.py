import sys

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

import re
from pathlib import Path
from typing import Union, Optional, get_origin, get_args
from argparse import ArgumentTypeError
from dataclasses import dataclass

@dataclass
class Info:
    """
    Class for keeping track structure of the info file.
    You can conceptually think of this class as the spec for the info.toml file.
    """
    name: str
    id: int
    vendor: str
    model: str
    px4_version: str
    px4_commit: Optional[str] = None

    custom_fw_version: Optional[str] = "0.0.0"
    components: Optional[Union[str, list[str]]] = None


class InfoManager:

    def __init__(self, input_info: Union[str, Path]) -> None:

        self.__content: str | None = None

        if isinstance(input_info, str):
            possible_path = Path(input_info)
            if possible_path.is_file():
                self.path = possible_path
            else:
                self.path = None
                self.__content = input_info
        elif isinstance(input_info, Path):
            if input_info.is_file():
                self.path = input_info
            else:
                raise FileNotFoundError(f"{input_info} is not a file.")

        else:
            raise TypeError(f"path must be str or Path, got {type(input_info).__name__}")

        self.__info_dict_raw: dict = self.__parse()
        self.__info = self.__load_dict(self.__info_dict_raw)


    def __parse(self) -> dict:
        try:
            if self.__content is not None:
                info = tomllib.loads(self.__content)
            elif self.path is not None:
                with self.path.open("r", encoding="utf-8") as f:
                    content = f.read()
                info = tomllib.loads(content)
            else:
                raise ValueError("No content or file path to parse from.")
        except tomllib.TOMLDecodeError as e:
            raise tomllib.TOMLDecodeError(f"Problem parsing TOML.\nTraceback:\n\n{e}")
        except Exception as e:
            raise Exception(f"Unexpected error: {e}")

        return info


    def __matches_type(self, value, expected_type) -> bool:
        """
        Return True if `value` conforms to `expected_type`.  Works for:
          - basic built-ins, e.g. str, int, float
          - Optional[...]  (i.e. Union[..., NoneType])
          - Union[...]     (checks any one branch)
          - list[SomeType]
          - dict[KeyType,ValueType]
          - (and will treat other non‐generic types as simple isinstance checks)
        """

        origin = get_origin(expected_type)
        args = get_args(expected_type)

        # 1) If it’s a Union (including Optional), try each branch:
        if origin is Union:
            # “Union[..., NoneType]” is the same as Optional[...]
            for branch in args:
                # Allow None if branch is NoneType
                if branch is type(None) and value is None:
                    return True
                # Otherwise, recursively check the other branch
                if branch is not type(None) and self.__matches_type(value, branch):
                    return True
            return False

        # 2) If it’s a list[T], first check isinstance(value, list), then each element matches T
        if origin is list:
            if not isinstance(value, list):
                return False
            (item_type,) = args
            for element in value:
                if not self.__matches_type(element, item_type):
                    return False
            return True

        # 3) If it’s a dict[K, V], check isinstance(value, dict) and each key/value pair matches
        if origin is dict:
            if not isinstance(value, dict):
                return False
            key_type, val_type = args
            for k, v in value.items():
                if not self.__matches_type(k, key_type) or not self.__matches_type(v, val_type):
                    return False
            return True

        return isinstance(value, expected_type)

    def __validation_types(self, info_dict) -> bool:

        for expected_key, expected_type in Info.__annotations__.items():
            if expected_key not in info_dict:
                # maybe is Optional
                if get_origin(expected_type) is Union and type(None) in get_args(expected_type):
                    continue
                else:
                    raise KeyError(f"{self.path}: Missing required field: {expected_key} of type {type(expected_type)}")

            value = info_dict[expected_key]

            if value is None:
                # If the field really is Optional[...] (Union[..., NoneType]), None is okay.
                if get_origin(expected_type) is Union and type(None) in get_args(expected_type):
                    continue
                else:
                    raise TypeError(f"Field '{expected_key}' must be of type {expected_type}, but got None.")

            if not self.__matches_type(value, expected_type):
                raise TypeError(
                    f"Field '{expected_key}' must be of type '{expected_type.__name__}'. "
                    f"Got value={value!r} (type={type(value).__name__})"
                )

        return True


    def __validation_content(self, info_dict) -> bool:

        if not re.fullmatch(r'v([0-9]+)\.([0-9]+)\.[0-9]+((-dev)|(-alpha[0-9]+)|(-beta[0-9]+)|(-rc[0-9]+))?$', info_dict["px4_version"]):
            raise ValueError(f"'px4_version' must be in format v<major>.<minor>.<patch>[-rc<rc>|-beta<beta>|-alpha<alpha>|-dev]. Got {info_dict['px4_version']}")

        if info_dict.get("custom_fw_version") is not None:
            if not re.fullmatch(r'([0-9]+)\.([0-9]+)\.([0-9]+)((-dev)|(-alpha[0-9]+)|(-beta[0-9]+)|(-?rc[0-9]+))?$', info_dict['custom_fw_version']):
                raise ValueError(f"'custom_fw_version' must be semantic version <major>.<minor>.<patch>[-rc<rc>|-beta<beta>|-alpha<alpha>|-dev]. Got {info_dict['custom_fw_version']}")

        return True


    def __load_dict(self, info_dict: dict) -> Info:

        self.__validation_types(info_dict)

        self.__validation_content(info_dict)

        return Info(**info_dict)

    def get_info(self) -> Info:
        return self.__info

    @property
    def info(self) -> dict:
        return self.__info_dict_raw

def load_info(info: Union[str, Path]) -> InfoManager:
    """
    Load info.toml file from path.
    """
    return InfoManager(info)

def load_info_dict(info: Union[str, Path]) -> dict[str, dict]:
    """
    Load info.toml file from path.
    """
    return InfoManager(info).info
