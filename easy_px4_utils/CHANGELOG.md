# Changelog

## 0.1.0

- `easy-px4-utils` is created from a set of utility scripts in `easy-px4` and becomes its own independent package. The main idea behind this is that our other package [`eolab_drones`](https://github.com/EOLab-HSRW/drones-fw) needs the utilities to parse our drone [catalog](https://github.com/EOLab-HSRW/drones-fw/tree/main/eolab_drones/catalog), but **just the parsing utilities**, it does not need all the dependencies of `easy-px4` to generate firmwares.
