from typing import Union
from pathlib import Path
from easy_px4_utils import load_info_dict

from .backend.paths import PX4_DIR, WORK_DIR

def get_dir() -> Path:
    """
    Returns the working directory.
    """
    return WORK_DIR

def get_px4_dir() -> Path:
    """
    Returns path to directory containing PX4-Autopilot
    """
    return PX4_DIR

def get_build_dir() -> Path:
    """
    Returns the build directory used by easy_px4.
    """
    return PX4_DIR / "build"

def load_info(info: Union[str, Path]) -> dict[str, dict]:
    """
    Loads information from info.toml file.

    Args:
    - info: a multi line string, string path or Path to the file.
    """
    return load_info_dict(info)
