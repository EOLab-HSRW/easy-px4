# Easy PX4

[![Pytest Matrix](https://github.com/EOLab-HSRW/easy-px4/actions/workflows/test.yml/badge.svg)](https://github.com/EOLab-HSRW/easy-px4/actions/workflows/test.yml)
[![Deploy Multi-Arch Docker Image](https://github.com/EOLab-HSRW/easy-px4/actions/workflows/deploy-container.yml/badge.svg)](https://github.com/EOLab-HSRW/easy-px4/actions/workflows/deploy-container.yml)

A simple tool to help to build custom firmware.

## Install

```
pip install git+https://github.com/EOLab-HSRW/easy-px4.git@main#egg=easy_px4
```

## How to Use

```text
easy-px4-template/
├─ info.toml (required)
├─ params.airframe (required)
├─ board.modules (required only in -physical- board builds)
├─ sitl.modules (required only in Software In The Loop builds)

components/
├─ script_1
├─ ...
├─ script_n
```

You can use the template structure from [easy-px4-template](https://github.com/EOLab-HSRW/easy-px4-template).


```sh
easy_px4 build --type firmware --path ./easy-px4-template --comps ./easy-px4-template/components/
```


Description of files:
- `info.toml`: contains meta information required for setup and firmware generation.
- `params.airframe`: Drone airframe configuration and default parameter values.
- `board.modules`: enable or disable modules in firmware. This is **always** agregated to the default PX4 modules of your `vendor` and `model` combination.
- `sitl.modules`: enable or disable modules in firmware.

On `info.toml` values
- `name` (mandatory string): name of the drone. This should be alpanumeric and underscore is the only allowed symbol.
- `id` (mandatory integer): number to unambiguously and uniquely identify the airframe. This is map to the parameter [`SYS_AUTOSTART`](https://docs.px4.io/main/en/advanced_config/parameter_reference.html#SYS_AUTOSTART), to avoid collision pick a number from `[22000, 22999]` as this range is reserved by PX4 specifically for the purpose of custom airframes.
- `vendor` (mandatory string): The manufacturer of the board, e.g. `px4`, `nxp`, etc.
- `model` (mandatory string): The board model: `sitl`, `fmu-v4`, `fmu-v5`, etc.
- `px4_version` (mandatory string): PX4 version to be compiled in format `v<major>.<minor>.<patch>[-rc<rc>|-beta<beta>|-alpha<alpha>|-dev]`. Do not forget to add the lowercase `v` letter prependix the semantic version.
- `px4_commit` (optional string): This parameter **takes precedence** over `px4_version`. If set, `px4_version` (which remains mandatory) is used solely for annotation purposes and does not represent a tagged version of PX4.
- `custom_fw_version` (optional string): Default `0.0.0`. This option allows you to enter your custom firmware version in the format `<major>.<minor>.<patch>[-rc<rc>|-beta<beta>|-alpha<alpha>|-dev]`.
- `components` (optional string or list of strings): Default `None`. Add startup scripts into the firmware that can be use later to initialize components.:

## Why?

This tool was born from the need to generate custom firmwares for the self-built drone in the [EOLab - HSRW](https://drones.eolab.de/).

Why generate custom firmware? 

Sometimes you need modules that are not enabled in the uptream versions of PX4 requiring you to compile the firmware from source to enable modules. An example of this is the module `CONFIG_DRIVERS_RC_CRSF_RC` to enable the [crsf_rc](https://docs.px4.io/main/en/modules/modules_driver_radio_control.html#crsf-rc) driver (Crossfire) and although there have been questions [Make CRSF telemetry protocol by default on new builds](https://github.com/PX4/PX4-Autopilot/issues/23829) about the possibility of including this module uptream, the reallity is that the process of adding things to uptream simply takes time.

We want not just the generate firmwares but also keep track of the changes on the files used for the generation.
- Fork: Making a Fork repository of the [PX4-Autopilot](https://github.com/PX4/PX4-Autopilot) and simply adding all the files directly requires constant synchronization of the Fork and the git history of the changes made to our configuration files is mixed with the PX4 commit history.

This tool was born from the need to generate custom firmwares for drones.

Why is this package restricted to just linux systems?
This tool simply automates the setup of your files and still depends on PX4 build system, so you need the PX4 toolchain, which is recommended on Linux (Ubuntu). See [Setting up a Developer Environment (Toolchain)](https://docs.px4.io/main/en/dev_setup/dev_env.html).

TODO:
- [ ] Add support to `dds_topics.yaml` customization.
- [ ] Add support to easily start sitl
- [ ] Add support to clean build cache
