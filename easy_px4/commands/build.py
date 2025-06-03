import sys

import shutil
import subprocess
from pathlib import Path
from argparse import ArgumentParser, Namespace
from .command import Command
from ..utils.directory import load_directory, valid_dir_path
from ..paths import PX4_DIR
from ..runner import run_command




class BuildCommand(Command):
    """
    Build command to handled the build of PX4.
    We make a distintion on:
    - firmware: binary that is flash into the flight controller
    - sitl: binary running for simulation (Software in the Loop)

    Clearly both are firmware but the terminology distintion is mainly
    to create a mental separation between the one running on the FMU and 
    the one for development.

    The way how the build command works is by getting:
    - type: define the type of build
    - path: a path to a directory containing the files
        - info.toml: information specific to the drone
        - board.modules: list of modules to enable on hardware
        - sitl.modules: list of modules to enable for simulation
        - parms.airframe: airframe file defining all the parameter for the drone
    """
    cmd_name = "build"

    BUILD_TYPES = [
        "firmware",
        "sitl"
    ]

    def __init__(self) -> None:
        super().__init__()
        self.target_tag = None
        self.original_tag = None
        self.commit_hash = None

    def add_arguments(self, parser: ArgumentParser) -> None:

        parser.add_argument("--type",
                            required=True,
                            type=str.lower,
                            choices=self.BUILD_TYPES,
                            help="type of build"
                            )

        parser.add_argument("--path",
                            type=valid_dir_path,
                            required=True,
                            help="Path to the directory containing all the firmware files")

        parser.add_argument("--output",
                            default=".",
                            type=valid_dir_path,
                            help="Path to the output directory")


        parser.add_argument("--dry-run",
                            action="store_true",
                            help="Run build without actually building anything (for testing)")

        # Parameters check
        # see if the parameter is set to default
        # check if the parameter exist ?
        parser.add_argument("--params-check",
                            default=False,
                            type=bool,
                            help="Parameter check. Check if the parameter are set with the right default-value")

        # caching ?
        # clean run ?


    def __prepend_insertion(self, file: Path, match: str, insert: str):

        if not file.is_file():
            self.logger.error(f"the provided path is not a file. Got path {file}")
            sys.exit(1)

        temp = file.parent / f"{file.stem}.tmp"

        with file.open("r") as infile, temp.open("w") as outfile:
            for line in infile:
                if match in line:
                    outfile.write(insert + '\n')
                outfile.write(line)

        temp.replace(file)


    def execute(self, args: Namespace) -> None:

        directory = load_directory(args.path)

        info = directory.info

        # STEP: fetch all the tags
        fetch_res = run_command(['git', 'fetch', '--tags', '--force'], cwd=PX4_DIR)
        if fetch_res['returncode'] != 0:
            self.logger.error(f"Failed to fetch tags: {fetch_res['stderr']}")
            sys.exit(1)

        # STEP: composing the correct tag before checkout
        self.original_tag = ""
        if any(word in info.custom_fw_version for word in ["beta", "alpha", "rc"]):
            self.original_tag = f"{info.px4_version}-{info.custom_fw_version}"
            self.target_tag = self.original_tag
        else:
            self.original_tag = info.px4_version
            self.target_tag  = f"{info.px4_version}-{info.custom_fw_version}"

        # STEP: checkout to version
        self.logger.info(f"Checking out to version {self.original_tag}")
        git_checkout = run_command(['git', 'checkout', self.original_tag], cwd=PX4_DIR)
        if git_checkout['returncode'] != 0:
            self.logger.error(f"Failed to checkout to {self.original_tag}. Make sure if a valid px4 version. {git_checkout['stderr']}")
            sys.exit(1)

        self.logger.info("Syncronizing submodules")
        run_command(["git", "submodule", "deinit", "-f", "--all"], cwd=PX4_DIR)
        run_command(["git", "submodule", "sync", "--recursive"], cwd=PX4_DIR)
        run_command(["git", "submodule", "update", "--init", "--recursive"], cwd=PX4_DIR)

        # STEP: get commit hash
        self.commit_hash = run_command(['git', 'rev-list', '-n', '1', self.original_tag], cwd=PX4_DIR)["stdout"]

        run_command(['git', 'tag', '-d', self.original_tag], cwd=PX4_DIR, check=True)

        run_command(['git', 'tag', self.target_tag, self.commit_hash], cwd=PX4_DIR, check=True)

        if args.type == "firmware":
            tooling_cmd = ["bash", "./Tools/setup/ubuntu.sh", "--no-sim-tools"]
            target_px4board = PX4_DIR / "boards"/ info.vendor / info.model / f"{info.name}.px4board"
            airframes = PX4_DIR / "ROMFS" / "px4fmu_common" / "init.d" / "airframes"
            target = f"{info.vendor}_{info.model}_{info.name}"
        elif args.type == "sitl":
            tooling_cmd = ["bash", "./Tools/setup/ubuntu.sh"]
            target_px4board = PX4_DIR / "boards"/ info.vendor / "sitl" / f"{info.name}.px4board"
            airframes = PX4_DIR / "ROMFS" / "px4fmu_common" / "init.d-posix" / "airframes" 
            target = f"{info.vendor}_sitl_{info.name}"


        self.logger.info("Install PX4 tooling...")
        run_command(tooling_cmd, cwd=PX4_DIR)

        shutil.copy2(args.path / directory.modules_file, target_px4board)

        airframes_CMakeLists = airframes / "CMakeLists.txt"
        airframe_file = f"{info.id}_{info.name}"
        target_airframe = airframes / airframe_file

        shutil.copy2(args.path / directory.params_file, target_airframe)

        self.__prepend_insertion(airframes_CMakeLists, "[4000, 4999] Quadrotor x", airframe_file)

        CMakeLists_init = PX4_DIR / "ROMFS" / "px4fmu_common" / "init.d" / "CMakeLists.txt"

        if info.components is not None:
            self.logger.info("No components found. Skipping components.")
            components_normalized = " ".join(info.components) if isinstance(info.components, list) else info.components
            self.__prepend_insertion(CMakeLists_init, "rcS", components_normalized)

        self.logger.info(f"Ready to build custom firmware for target {target}")
        run_command(["make", "clean"], cwd=PX4_DIR)
        build_px4 = run_command(["make", target], 
                                cwd=PX4_DIR,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT,
                                text=True,  # or encoding='utf-8'
                                capture_output=False
                                )

        if build_px4['returncode'] != 0:
            self.logger.error(f"Failed to build target {target}. {build_px4['stderr']} {build_px4['stdout']} {build_px4['error']}")
            sys.exit(1)


        # shutil.copy2(PX4_DIR / "build" / target / f"{target}.px4", args.output / f"{info.name}_{info.custom_fw_version}.px4")

        # cleaning steps

        # target_px4board.unlink() # remove file

    def cleanup(self):
        # can I do cleaning by using just git ? does it affect the build folder ?
        run_command(['git', 'tag', '-d', self.target_tag], cwd=PX4_DIR, check=True)
        run_command(['git', 'tag', self.original_tag, self.commit_hash], cwd=PX4_DIR, check=True)
        # run_command(['git', 'restore', '.'], cwd=PX4_DIR, check=True)


        """
        force cleaning:

        # 1. Move the build/ folder out of the repo temporarily
mv build ../build-temp

# 2. Remove all untracked files and folders (force + directories)
git clean -fdx

# 3. Reset tracked files to exactly match HEAD
git reset --hard HEAD

# 4. Move the build/ folder back
mv ../build-temp build

        """
