from typing import Union
from pathlib import Path
from .utils.info import load_info_dict

from .paths import PX4_DIR, WORK_DIR

def get_dir() -> Path:
    """
    Return the working directory.
    """
    return WORK_DIR

def get_px4_dir() -> Path:
    """
    Return path to directory containing PX4-Autopilot
    """
    return PX4_DIR

def load_info(info: Union[str, Path]) -> dict[str, dict]:
    """
    Load information from info.toml file.

    Args:
    - info: a multi line string, string path or Path to the file.
    """
    return load_info_dict(info)

