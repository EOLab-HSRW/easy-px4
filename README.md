# Easy PX4

A simple tool to help to build custom firmware.

## How to Use

```text
your_config/
├─ info.toml (required)
├─ params.airframe (required)
├─ board.modules (required only in -physical- board builds)
├─ sitl.modules (required only in Software In The Loop builds)
```

Description of files:
- `info.toml`: contains meta information required for setup and firmware generation.
- `params.airframe`: Drone airframe configuration and default parameter values.
- `board.modules`: enable or disable modules in firmware. This is always agregated to the default modules
- `sitl.modules`: enable or disable modules in firmware.

On `info.toml` values
- `name` (mandatory string): name of the drone. This should be alpanumeric and underscore is the only allowed symbol.
- `id` (mandatory integer): number to unambiguously and uniquely identify the airframe. This is realed to the parameter [`SYS_AUTOSTART`](https://docs.px4.io/main/en/advanced_config/parameter_reference.html#SYS_AUTOSTART), to avoid collision pick a number from `[22000, 22999]` as this range is reserved by PX4 specifically for this purpose.
- `vendor` (mandatory string): The manufacturer of the board, e.g. `px4`, `nxp`, etc.
- `model` (mandatory string): The board model: `sitl`, `fmu-v4`, `fmu-v5`, etc.
- `px4_version` (mandatory string): PX4 version to be compiled in format `v<int>.<int>.<int>`. Do not forget to add the lowercase `v` letter prependix the semantic version.
- `custom_fw_version` (optional string): Default `0.0.0`. This option allows you to enter your custom firmware version, but also allows you to compile specific PX4 versions such as `rc1`, `beta1`, `alpha`, in `[rc|beta|alpha]<int>` format.
- `default_components` (optional string or list of strings): Default `None`. Add startup scripts into the firmware that can be use later to initialize components.:

(harley's note) planning to remove `[components]`

## Why?

This tool was born from the need to generate custom firmwares for the self-built drone in the [EOLab - HSRW](https://drones.eolab.de/).

Why generate custom firmware? 

Sometimes you need modules that are not enabled in the uptream versions of PX4 requiring you to compile the firmware from source to enable modules. An example of this is the module `CONFIG_DRIVERS_RC_CRSF_RC` to enable the [crsf_rc](https://docs.px4.io/main/en/modules/modules_driver_radio_control.html#crsf-rc) driver (Crossfire) and although there have been questions [Make CRSF telemetry protocol by default on new builds](https://github.com/PX4/PX4-Autopilot/issues/23829) about the possibility of including this uptream module the process of adding things to uptream simply takes time.

We want not just the generate firmwares but also keep track of the changes on the files used for the generation.
- Fork: Making a Fork repository of the [PX4-Autopilot](https://github.com/PX4/PX4-Autopilot) and simply adding all the files directly requires constant synchronization of the Fork and the git history of the changes made to our configuration files is mixed with the PX4 commit history.

This tool was born from the need to generate custom firmwares for drones.

Why is this package restricted to just linux systems?
This tool simply automates the setup of your files and still depends on PX4 build system, so you need the PX4 toolchain, which is recommended on Linux (Ubuntu). See [Setting up a Developer Environment (Toolchain)](https://docs.px4.io/main/en/dev_setup/dev_env.html).
