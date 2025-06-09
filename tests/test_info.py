from pathlib import Path
import tomli
import pytest
import easy_px4

def test_load_info_good():

    info = easy_px4.load_info("""
        name = "drone"
        id = 12345
        vendor = "px4"
        model = "fmu-v3"
        px4_version = "v1.15.4"
        custom_fw_version = "0.0.2"
    """)

    info_test_file = Path(__file__).resolve().parent.parent / "demos/protoflyer/info.toml"
    easy_px4.load_info(info_test_file)
    easy_px4.load_info(str(info_test_file))

def test_load_info_missing_key():

    with pytest.raises(KeyError):
        easy_px4.load_info("""
            name = "drone"
            id = 12345
            vendor = "px4"
            px4_version = "v1.15.4"
            custom_fw_version = "0.0.2"
        """)

def test_load_info_components():
    info = easy_px4.load_info("""
        name = "drone"
        id = 12345
        vendor = "px4"
        model = "fmu-v3"
        px4_version = "v1.15.4"
        custom_fw_version = "0.0.2"
        components = "some_component"
    """)

    info = easy_px4.load_info("""
        name = "drone"
        id = 12345
        vendor = "px4"
        model = "fmu-v3"
        px4_version = "v1.15.4"
        custom_fw_version = "0.0.2"
        components = ["some_component", "other_component"]
    """)

def test_load_info_bad():

    with pytest.raises(tomli._parser.TOMLDecodeError):
        # incorrect formating name
        easy_px4.load_info("""
            name = drone
            id = '12345'
            vendor = "px4"
            model = "fmu-v3"
            px4_version = "v1.15.4"
            custom_fw_version = "0.0.2"
        """)


    with pytest.raises(TypeError):
        easy_px4.load_info("""
            name = 'drone'
            id = '12345'
            vendor = "px4"
            model = "fmu-v3"
            px4_version = "v1.15.4"
            custom_fw_version = "0.0.2"
        """)

    with pytest.raises(tomli._parser.TOMLDecodeError):
        # incorrect formating vendor
        easy_px4.load_info("""
            name = drone
            id = '12345'
            vendor = px4
            model = "fmu-v3"
            px4_version = "v1.15.4"
            custom_fw_version = "0.0.2"
        """)

    with pytest.raises(TypeError):
        # extra keys that is not part of the info structure
        easy_px4.load_info("""
            name = "drone"
            id = 12345
            vendor = "px4"
            model = "fmu-v3"
            px4_version = "v1.15.4"
            custom_fw_version = "0.0.2"
            extra = "stuff"
        """)

def test_load_info_px4_version():
    """
    test for correct format of px4_version
    """

    easy_px4.load_info("""
        name = "drone"
        id = 12345
        vendor = "px4"
        model = "fmu-v3"
        px4_version = "v1.15.4"
        custom_fw_version = "1.2.3"
    """)

    easy_px4.load_info("""
        name = "drone"
        id = 12345
        vendor = "px4"
        model = "fmu-v3"
        px4_version = "v1.15.4-beta1"
        custom_fw_version = "1.2.3"
    """)

    easy_px4.load_info("""
        name = "drone"
        id = 12345
        vendor = "px4"
        model = "fmu-v3"
        px4_version = "v1.15.4-alpha3"
        custom_fw_version = "1.2.3"
    """)

    easy_px4.load_info("""
        name = "drone"
        id = 12345
        vendor = "px4"
        model = "fmu-v3"
        px4_version = "v1.15.4-rc22"
        custom_fw_version = "1.2.3"
    """)

    easy_px4.load_info("""
        name = "drone"
        id = 12345
        vendor = "px4"
        model = "fmu-v3"
        px4_version = "v1.15.4-dev"
        custom_fw_version = "1.2.3"
    """)

    with pytest.raises(ValueError):
        easy_px4.load_info("""
            name = "drone"
            id = 12345
            vendor = "px4"
            model = "fmu-v3"
            px4_version = "1.15.4"
            custom_fw_version = "0.0.2"
        """)

    with pytest.raises(ValueError):
        easy_px4.load_info("""
            name = "drone"
            id = 12345
            vendor = "px4"
            model = "fmu-v3"
            px4_version = "v1.15.4.0"
            custom_fw_version = "0.0.2"
        """)

    # missing int
    with pytest.raises(ValueError):
        easy_px4.load_info("""
            name = "drone"
            id = 12345
            vendor = "px4"
            model = "fmu-v3"
            px4_version = "v1.15.4-beta"
            custom_fw_version = "0.0.2"
        """)

    with pytest.raises(ValueError):
        easy_px4.load_info("""
            name = "drone"
            id = 12345
            vendor = "px4"
            model = "fmu-v3"
            px4_version = "v1.15.4-rc"
            custom_fw_version = "0.0.2"
        """)

    with pytest.raises(ValueError):
        easy_px4.load_info("""
            name = "drone"
            id = 12345
            vendor = "px4"
            model = "fmu-v3"
            px4_version = "v1.15.4-alpha"
            custom_fw_version = "0.0.2"
        """)

    # dev with int
    with pytest.raises(ValueError):
        easy_px4.load_info("""
            name = "drone"
            id = 12345
            vendor = "px4"
            model = "fmu-v3"
            px4_version = "v1.15.4-dev1"
            custom_fw_version = "0.0.2"
        """)

    with pytest.raises(ValueError):
        easy_px4.load_info("""
            name = "drone"
            id = 12345
            vendor = "px4"
            model = "fmu-v3"
            px4_version = "1.14"
            custom_fw_version = "0.0.2"
        """)

    with pytest.raises(ValueError):
        easy_px4.load_info("""
            name = "drone"
            id = 12345
            vendor = "px4"
            model = "fmu-v3"
            px4_version = "latest"
            custom_fw_version = "0.0.2"
        """)

def test_load_info_custom_fw_version():
    easy_px4.load_info("""
        name = "drone"
        id = 12345
        vendor = "px4"
        model = "fmu-v3"
        px4_version = "v1.15.4"
        custom_fw_version = "1.2.3"
    """)

    easy_px4.load_info("""
        name = "drone"
        id = 12345
        vendor = "px4"
        model = "fmu-v3"
        px4_version = "v1.15.4"
        custom_fw_version = "1.2.3-rc2"
    """)

    easy_px4.load_info("""
        name = "drone"
        id = 12345
        vendor = "px4"
        model = "fmu-v3"
        px4_version = "v1.15.4"
        custom_fw_version = "1.2.3-alpha2"
    """)

    easy_px4.load_info("""
        name = "drone"
        id = 12345
        vendor = "px4"
        model = "fmu-v3"
        px4_version = "v1.15.4"
        custom_fw_version = "1.2.3-beta2"
    """)

    easy_px4.load_info("""
        name = "drone"
        id = 12345
        vendor = "px4"
        model = "fmu-v3"
        px4_version = "v1.15.4"
        custom_fw_version = "1.2.3-dev"
    """)

    with pytest.raises(ValueError):
        easy_px4.load_info("""
            name = "drone"
            id = 12345
            vendor = "px4"
            model = "fmu-v3"
            px4_version = "v1.15.4"
            custom_fw_version = "0.2.0.0"
        """)

    with pytest.raises(ValueError):
        easy_px4.load_info("""
            name = "drone"
            id = 12345
            vendor = "px4"
            model = "fmu-v3"
            px4_version = "v1.15.4"
            custom_fw_version = "0.2"
        """)
