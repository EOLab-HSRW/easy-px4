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
                            help="Type of build."
                            )

        parser.add_argument("--path",
                            type=valid_dir_path,
                            required=True,
                            help="Directory with build configuration files.")

        parser.add_argument("--comps",
                            type=valid_dir_path,
                            help="Directory with components for build filesystem.")

        parser.add_argument("--output",
                            default=".",
                            type=valid_dir_path,
                            help="Output directory (firmware only).")

        parser.add_argument("--dry-run",
                            action="store_true",
                            help="Run build without actually building anything (for testing)")

        parser.add_argument("--clean-run",
                            action="store_true",
                            help="Clean build artifacts before build.")

        parser.add_argument("--overwrite",
                            action="store_true",
                            help="Overwrite existing build if present.")

        parser.add_argument("--params-check",
                            action="store_true",
                            help="Check that parameters have correct default values.")


    def __prepend_insertion(self, file: Path, match: str, insert: str):

        if not file.is_file():
            self.logger.error(f"Invalid file path: {file}")
            sys.exit(1)

        temp = file.parent / f"{file.stem}.tmp"

        with file.open("r") as infile, temp.open("w") as outfile:
            for line in infile:
                if match in line:
                    outfile.write(insert + '\n')
                outfile.write(line)

        temp.replace(file)


    def __validate_comps(self, components, comps_path: Path) -> bool:
        files = {f.name for f in comps_path.glob('*') if f.is_file()}
        missing = [comp for comp in components if comp not in files]

        if missing:
            self.logger.error(f"Missing components {missing} in {comps_path.absolute()}")
            sys.exit(1)
        return True


    def __setup_git(self, info) -> None:

        self.logger.debug(f"Fetching tags")
        fetch_res = run_command(['git', 'fetch', '--tags', '--force'], cwd=PX4_DIR)
        if fetch_res['returncode'] != 0:
            self.logger.error(f"Failed to fetch tags: {fetch_res['stderr']}")
            sys.exit(1)

        self.logger.debug(f"Starting tag composition")
        self.original_tag = info.px4_version
        if any(word in info.custom_fw_version for word in ["beta", "alpha", "rc"]):
            self.original_tag = f"{info.px4_version}-{info.custom_fw_version}"
            self.target_tag = self.original_tag
        else:
            self.target_tag  = f"{info.px4_version}-{info.custom_fw_version}"
        self.logger.debug(f"{self.original_tag} -> {self.target_tag}")

        self.logger.info(f"Checking out to version {self.original_tag}")
        git_checkout = run_command(['git', 'checkout', self.original_tag], cwd=PX4_DIR)
        if git_checkout['returncode'] != 0:
            self.logger.error(f"Failed to checkout to {self.original_tag}. Make sure is a valid px4 version. {git_checkout['stderr']}")
            sys.exit(1)

        self.logger.info("Syncronizing submodules")
        run_command(["git", "submodule", "deinit", "-f", "--all"], cwd=PX4_DIR)
        run_command(["git", "submodule", "sync", "--recursive"], cwd=PX4_DIR)
        run_command(["git", "submodule", "update", "--init", "--recursive"], cwd=PX4_DIR)

        self.commit_hash = run_command(['git', 'rev-list', '-n', '1', self.original_tag], cwd=PX4_DIR)["stdout"]
        run_command(['git', 'tag', '-d', self.original_tag], cwd=PX4_DIR, check=True)
        run_command(['git', 'tag', self.target_tag, self.commit_hash], cwd=PX4_DIR, check=True)



    def execute(self, args: Namespace) -> None:

        self.logger.debug(f"Loading directory {args.path} as {args.type}")
        directory = load_directory(args.path, args.type)

        info = directory.info
        self.logger.debug(f"Info: {info}")

        tooling_cmd, px4board, init_romfs_dir, airframe_match, target = {
            "firmware": (
                ["bash", "./Tools/setup/ubuntu.sh", "--no-sim-tools"],
                PX4_DIR / "boards" / info.vendor / info.model / f"{info.name}.px4board",
                PX4_DIR / "ROMFS" / "px4fmu_common" / "init.d",
                "[4000, 4999] Quadrotor x",
                f"{info.vendor}_{info.model}_{info.name}"
            ),
            "sitl": (
                ["bash", "./Tools/setup/ubuntu.sh"],
                PX4_DIR / "boards" / info.vendor / "sitl" / f"{info.name}.px4board",
                PX4_DIR / "ROMFS" / "px4fmu_common" / "init.d-posix",
                "# [22000, 22999] Reserve for custom models",
                f"{info.vendor}_sitl_{info.name}"
            )
        }[args.type]

        if not args.overwrite and (PX4_DIR / "build" / target).exists():
            self.logger.info(f"Target {target} already built. Use --overwrite to rebuild.")
            sys.exit(0)

        self.__setup_git(info)

        self.logger.info("Installing PX4 tooling...")
        run_command(tooling_cmd, cwd=PX4_DIR)

        shutil.copy2(args.path / directory.modules_file, px4board)

        airframes = init_romfs_dir / "airframes"
        components_insert_dir = PX4_DIR / "ROMFS" / "px4fmu_common" / "init.d"
        cmake_components = components_insert_dir / "CMakeLists.txt"

        airframe_file = f"{info.id}_{info.name}"
        target_airframe = airframes / airframe_file
        cmake_airframes = airframes / "CMakeLists.txt"

        shutil.copy2(args.path / directory.params_file, target_airframe)
        self.__prepend_insertion(cmake_airframes, airframe_match, airframe_file)

        if args.comps is not None:
            if info.components is not None and self.__validate_comps(info.components, args.comps):
                for component in info.components:
                    shutil.copy2(args.comps / component, components_insert_dir / component)
                components_normalized = " ".join(info.components) if isinstance(info.components, list) else info.components
                self.__prepend_insertion(cmake_components, "rcS", components_normalized)
            else:
                self.logger.warn(f"No components defined in {directory.info_file}, skipping components population.")
        else:
            if info.components is not None:
                self.logger.error(f"{directory.info_file} defines components but no --comps provided.")
                sys.exit(1)


        self.logger.info(f"Building firmware for target {target}")

        if args.clean_run:
            run_command(["make", "clean"], cwd=PX4_DIR)

        build_px4 = run_command(
            ["make", target],
            cwd=PX4_DIR,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            capture_output=False
        )

        if build_px4['returncode'] != 0:
            self.logger.error(f"Build failed for {target}. {build_px4.get('stderr', '')}")
            sys.exit(1)


        # shutil.copy2(PX4_DIR / "build" / target / f"{target}.px4", args.output / f"{info.name}_{info.custom_fw_version}.px4")

        # cleaning steps

        # target_px4board.unlink() # remove file

    def cleanup(self):
        self.logger.debug(f"Restoring tag to {self.original_tag}.")
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
