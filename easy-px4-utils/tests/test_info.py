import sys
from pathlib import Path

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

import pytest
import easy_px4_utils

def test_load_info_good():

    info = easy_px4_utils.load_info("""
        name = "drone"
        id = 12345
        vendor = "px4"
        model = "fmu-v3"
        px4_version = "v1.15.4"
        custom_fw_version = "0.0.2"
    """)

    info = easy_px4_utils.load_info("""
        name = "drone"
        id = 12345
        vendor = "px4"
        model = "fmu-v3"
        px4_version = "v1.15.4"
        px4_commit = "main"
        custom_fw_version = "0.0.2"
    """)

    info_test_file = Path(__file__).resolve().parent.parent / "demos/protoflyer/info.toml"
    easy_px4_utils.load_info(info_test_file)
    easy_px4_utils.load_info(str(info_test_file))

def test_load_info_missing_key():

    with pytest.raises(KeyError):
        easy_px4_utils.load_info("""
            name = "drone"
            id = 12345
            vendor = "px4"
            px4_version = "v1.15.4"
            custom_fw_version = "0.0.2"
        """)


def test_load_info_single_component():
    info = easy_px4_utils.load_info("""
        name = "drone"
        id = 12345
        vendor = "px4"
        model = "fmu-v3"
        px4_version = "v1.15.4"
        custom_fw_version = "0.0.2"
        components = "some_component"
    """)

def test_load_info_list_components():
    info = easy_px4_utils.load_info("""
        name = "drone"
        id = 12345
        vendor = "px4"
        model = "fmu-v3"
        px4_version = "v1.15.4"
        custom_fw_version = "0.0.2"
        components = ["some_component", "other_component"]
    """)

def test_load_info_bad():

    with pytest.raises(tomllib.TOMLDecodeError):
        # incorrect formating name
        easy_px4_utils.load_info("""
            name = drone
            id = "12345"
            vendor = "px4"
            model = "fmu-v3"
            px4_version = "v1.15.4"
            custom_fw_version = "0.0.2"
        """)


    with pytest.raises(TypeError):
        easy_px4_utils.load_info("""
            name = 'drone'
            id = '12345'
            vendor = "px4"
            model = "fmu-v3"
            px4_version = "v1.15.4"
            custom_fw_version = "0.0.2"
        """)

    with pytest.raises(tomllib.TOMLDecodeError):
        # incorrect formating vendor
        easy_px4_utils.load_info("""
            name = drone
            id = '12345'
            vendor = px4
            model = "fmu-v3"
            px4_version = "v1.15.4"
            custom_fw_version = "0.0.2"
        """)

    with pytest.raises(TypeError):
        # extra keys that is not part of the info structure
        easy_px4_utils.load_info("""
            name = "drone"
            id = 12345
            vendor = "px4"
            model = "fmu-v3"
            px4_version = "v1.15.4"
            custom_fw_version = "0.0.2"
            extra = "stuff"
        """)


valid_px4_versions = [
    "v1.15.4",
    "v1.15.4-beta1",
    "v1.15.4-alpha3",
    "v1.15.4-rc22",
    "v1.15.4-dev",
]

@pytest.mark.parametrize("version", valid_px4_versions)
def test_valid_px4_versions(version):
    easy_px4_utils.load_info(f"""
        name = "drone"
        id = 12345
        vendor = "px4"
        model = "fmu-v3"
        px4_version = "{version}"
        custom_fw_version = "1.2.3"
    """)

invalid_px4_versions = [
    "v1.15.4.0",
    "v1.15.4-beta",
    "v1.15.4-rc",
    "v1.15.4-alpha",
    "v1.15.4-dev1",
    "1.14",
    "latest",
    "1.15.4",
]

@pytest.mark.parametrize("version", invalid_px4_versions)
def test_invalid_px4_versions(version):
    with pytest.raises(ValueError):
        easy_px4_utils.load_info(f"""
            name = "drone"
            id = 12345
            vendor = "px4"
            model = "fmu-v3"
            px4_version = "{version}"
            custom_fw_version = "0.0.2"
        """)

valid_custom_fw_versions = [
    "1.2.3",
    "1.2.3-rc2",
    "1.2.3-alpha2",
    "1.2.3-beta2",
    "1.2.3-dev",
]

@pytest.mark.parametrize("version", valid_custom_fw_versions)
def test_valid_custom_fw_versions(version):
    easy_px4_utils.load_info(f"""
        name = "drone"
        id = 12345
        vendor = "px4"
        model = "fmu-v3"
        px4_version = "v1.15.4"
        custom_fw_version = "{version}"
    """)


invalid_custom_fw_versions = [
    "0.2.0.0",
    "0.2",
]

@pytest.mark.parametrize("version", invalid_custom_fw_versions)
def test_invalid_custom_fw_versions(version):
    with pytest.raises(ValueError):
        easy_px4_utils.load_info(f"""
            name = "drone"
            id = 12345
            vendor = "px4"
            model = "fmu-v3"
            px4_version = "v1.15.4"
            custom_fw_version = "{version}"
        """)
