# Easy PX4

[![Pytest Matrix](https://github.com/EOLab-HSRW/easy-px4/actions/workflows/test.yml/badge.svg)](https://github.com/EOLab-HSRW/easy-px4/actions/workflows/test.yml)
[![Deploy Multi-Arch Docker Image](https://github.com/EOLab-HSRW/easy-px4/actions/workflows/deploy-container.yml/badge.svg)](https://github.com/EOLab-HSRW/easy-px4/actions/workflows/deploy-container.yml)

A simple automation tool to build [PX4](https://github.com/PX4/PX4-Autopilot) firmware for custom airframes.

## Install

(Recommended) Using docker:

```
docker pull ghcr.io/eolab-hsrw/easy-px4:ubuntu-22.04
```

## How to Use

```sh
easy_px4 build --type firmware --path ./<path-to-your-settings>
```

To get the all the options, run:

```sh
easy_px4 build --help
```

## Documentation

To propagate your airframe configuration files and firmware settings, `easy_px4` expects an input folder containing the following files (case-sensitive filenames). For example, if you want to create a new airframe called `newbie`:

```text
newbie/
├─ info.toml (required)
├─ params.airframe (required)
├─ params.airframe.post (optional)
├─ board.modules (required only in --type firmware builds)
├─ sitl.modules (required only in --type sitl builds (software-in-the-loop))
```

Description of files:
- `info.toml`: contains meta information required for airframes identification and firmware generation.
- `params.airframe`: Drone airframe configuration and default parameter values. All the customization to your airframe goes here.
- `params.airframe.post`: Same as `params.airframe` but runs late during system boot.
- `board.modules`: enable or disable modules/drivers in firmware. This is **always** agregated to the **default PX4 modules** of your `vendor` and `model` combination as defined in your `info.toml`.
- `sitl.modules`: enable or disable modules/drivers in the software-in-the-loop (SITL) firmware.

### Info File

Here is a example of a `info.toml`:

```toml
name = "drache"
id = 22199
vendor = "px4"
model = "fmu-v6x"
px4_version = "v1.16.0-rc1"
custom_fw_version = "1.2.3"
components = ["radiomaster_tx16s"]
```


| Value | Requirement | Type | Description |
|-------|-------------|------|-------------|
| `name`              | mandatory | string | Name of the drone. This should be alpanumeric, and underscore is the only allowed symbol. |
| `id`                | mandatory | unsigned integer | Number to unambiguously and uniquely identify the airframe. This is map to the parameter [`SYS_AUTOSTART`](https://docs.px4.io/main/en/advanced_config/parameter_reference.html#SYS_AUTOSTART), to avoid collision pick a number from `[22000, 22999]` as this range is reserved by PX4 specifically for the purpose of custom airframes. Think of it as the "id" of your airframe within PX4 internal knowledge base. |
| `vendor`            | mandatory | string | The manufacturer of the board, e.g. `px4`, `nxp`, etc. |
| `model`             | mandatory | string | The board model: `sitl`, `fmu-v4`, `fmu-v5`, etc. |
| `px4_version`       | mandatory | string | PX4 version to be compiled in format `v<major>.<minor>.<patch>`. Do not forget to add the lowercase `v` letter prependix the semantic version, This essentially checks out PX4 release tags; therefore, beta, alpha, and release candidates are also possible. |
| `px4_commit`        | optional | string | This parameter **takes precedence** over `px4_version`. If set, `px4_version` (which remains mandatory) is used solely for annotation purposes and does not represent a tagged version of PX4. |
| `custom_fw_version` | optional | string | Default `0.0.0`. This option allows you to enter your custom firmware version in the format `<major>.<minor>.<patch>`. |
| `components`        | optional | string or list of strings | Default `None`. Add startup scripts into the firmware that can be use later to initialize components. |

## Components

"Components" are an `easy_px4`–specific concept. They are small configuration snippets that are aggregated into your firmware file system, so you can reference them from `params.airframe` or `params.airframe.post`.

A common use of "components" is sharing a set of common settings across multiple firmware builds. When running `easy_px4`, you can provide a path to your components, and `easy_px4` will check `info.toml` for the required ones. If all required components are found, they are aggregated into your firmware file system; otherwise, the build fails with an error indicating a missing required component.

Take the following folder as an example:

```text
components/
├─ common
├─ radiomaster_tx16s
├─ failsafe_settings
├─ ...
├─ component_n
```

You can build a firmware as:
```
easy_px4 build --type firmware --path ./<path-to-your-settings> --comps ./<path-to-your-components>
```

With this set of components, you can list them in `info.toml` and specify which ones are required for aggregation. In this example, `common` and `radiomaster_tx16s` will be added to the firmware:
```toml
name = "drache"
...
...
components = ["common", "radiomaster_tx16s"]
```

To use them, simply add the appropriate line to call them from either `params.airframe` or `params.airframe.post`:
```sh
...
...

. ${R}etc/init.d/common            # runs the common configuration
. ${R}etc/init.d/radiomaster_tx16s # runs the radiomaster_tx16s configuration

...
...
```


You can use the template structure from [easy-px4-template](https://github.com/EOLab-HSRW/easy-px4-template).

## Frequently Asked Questions

This tool was born from the need to generate custom firmwares for the self-built drones in the [EOLab - HSRW](https://drones.eolab.de/).

<details open>
  <summary>
  <strong>Why would I want to generate custom firmware(s) if I can use the uptream stable version of PX4?</strong>

  </summary>

> Sometimes you need modules or drivers that are not enabled in the uptream versions of PX4 by default, requiring you to compile the firmware from source to enable them. An example of this is the module `CONFIG_DRIVERS_RC_CRSF_RC` to enable the [crsf_rc](https://docs.px4.io/main/en/modules/modules_driver_radio_control.html#crsf-rc) driver (Crossfire) and although there have been questions [Make CRSF telemetry protocol by default on new builds](https://github.com/PX4/PX4-Autopilot/issues/23829) about the possibility of including this module uptream, the reallity is that the process of adding things to uptream simply takes time.

</details><br>

<details open>
  <summary>
  <strong>What problem is easy_px4 solving?</strong>

  </summary>

> `easy_px4` is a simple automation tool designed to make things easier.
>  1. **Self-contained configuration**: From the perspective of `easy_px4` all parameters and firmware settings are expected to be located in a single folder, rather than scattered across specific locations in the PX4 codebase, as would be necessary if you wanted to manually add the airframe to PX4.
> 2. **Independent versioning and decoupling**: Since `easy_px4` takes care of propagating your configs into PX4 you can create a repo containing only your settings and let `easy_px4` run the automation. Normally, if you fork PX4 and manually add all the required files to integrate your custom airframe into PX4 codebase, you would need constant synchronization with the upstream fork, and the git history of changes to your configuration files would be mixed with the PX4 commit history.
</details><br>

<details open>
  <summary>
  <strong>Why is easy_px4 restricted to just linux systems?</strong>

  </summary>

> `easy_px4` simply automates the setup of your files, still depends on PX4 build system, so you need the PX4 toolchain, which is recommended on Linux (Ubuntu). See [Setting up a Developer Environment (Toolchain)](https://docs.px4.io/main/en/dev_setup/dev_env.html).

</details><br>

## Contributions

See [CONTRIBUTING.md](./CONTRIBUTING.md).

TODO:
- [ ] Add support to `dds_topics.yaml` customization.
