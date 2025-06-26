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
        self.target_commit = None
        self.commit_hash = None
        self.renamed_tag = None

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
                            type=valid_dir_path,
                            help="Output directory (firmware only).")

        parser.add_argument("--dry-run",
                            action="store_true",
                            help="Run build without actually building anything (for testing)")

        parser.add_argument("--clean-run",
                            action="store_true",
                            help="Clean build artifacts before build.")

        parser.add_argument("--install-dependencies",
                            action="store_false",
                            help="Running official PX4 Tools/setup/ubuntu.sh script.")

        parser.add_argument("--overwrite",
                            action="store_true",
                            help="Overwrite existing build if present.")

        parser.add_argument("--msgs-output",
                            type=valid_dir_path,
                            help="Directory to store extracted PX4 msgs related to your build version.")

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

        self.logger.debug(f"PX4 Autopilo directory: {PX4_DIR}")
        run_command(['ls'], cwd=PX4_DIR, live=True, logger=self.logger)

        restore_res = run_command(['git', 'restore', '.'], live=True, logger=self.logger, cwd=PX4_DIR)
        if restore_res.returncode != 0:
            self.logger.error(f"Failed to restore repo: {restore_res.stderr}. {restore_res.stdout}")
            sys.exit(1)

        if info.px4_commit:
            self.logger.info("Found 'px4_commit'. Note that 'px4_commit' takes precedence over 'px4_version'. In this case 'px4_version' is used solely for annotation purposes and does not represent a tagged version of PX4.")

            self.target_commit = info.px4_commit
        else:
            self.logger.debug(f"Fetching PX4 tag: {info.px4_version}")
            fetch_res = run_command(['git', 'fetch', 'origin', 'tag', info.px4_version], cwd=PX4_DIR)
            if fetch_res.returncode != 0:
                self.logger.error(f"Failed to fetch tag {info.px4_version}: {fetch_res.stderr}, {fetch_res.stdout}")
                sys.exit(1)

            self.target_commit = info.px4_version

        self.logger.info(f"Checking out to: {self.target_commit}")
        git_checkout = run_command(['git', 'checkout', self.target_commit], cwd=PX4_DIR)
        if git_checkout.returncode != 0:
            self.logger.error(f"Failed to checkout to {self.target_commit}. Make sure is a valid px4 tag or commit. {git_checkout.stderr}")
            sys.exit(1)

        self.logger.info("Syncronizing submodules")
        run_command(["git", "submodule", "deinit", "-f", "--all"], cwd=PX4_DIR)
        run_command(["git", "submodule", "sync", "--recursive"], cwd=PX4_DIR)
        run_command(["git", "submodule", "update", "--init", "--recursive"], cwd=PX4_DIR)

        # self.commit_hash = run_command(['git', 'rev-list', '-n', '1', self.target_commit], cwd=PX4_DIR).stdout
        # self.logger.debug(f"Saving commit_hash: {self.commit_hash}")

        if not info.px4_commit:
            self.logger.debug(f"px4_commit not provided. We are in a tagged commit.")
            self.logger.debug(f"Removing original px4 tag: {info.px4_version}")
            run_command(['git', 'tag', '-d', info.px4_version], cwd=PX4_DIR, check=True)

        self.logger.debug(f"Re-tagging to add custom version")

        # =====================================================================================
        # Hacky way (for now) to make the tags work without changing the PX4 source code
        # or maybe I should start a conversation with PX4 to see what can we do ?
        px4_split = info.px4_version.split("-")

        if len(px4_split) > 1:
            px4_version = px4_split[0]
            px4_release = px4_split[1]
            self.renamed_tag = f"{px4_version}-{info.custom_fw_version.split('-')[0]}-{px4_release}"
        else:
            self.renamed_tag = f"{px4_split[0]}-{info.custom_fw_version.split('-')[0]}"
        # =====================================================================================

        self.logger.debug(f"Re-tagging: {info.px4_version} -> {self.renamed_tag}")

        run_command(['git', 'tag', self.renamed_tag], cwd=PX4_DIR, check=True)


    def execute(self, args: Namespace) -> None:

        self.logger.debug(f"Loading directory {args.path} as {args.type}")
        directory = load_directory(args.path, args.type)

        info = directory.get_info()
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
                PX4_DIR / "boards" / "px4" / "sitl" / f"{info.name}.px4board",
                PX4_DIR / "ROMFS" / "px4fmu_common" / "init.d-posix",
                "# [22000, 22999] Reserve for custom models",
                f"px4_sitl_{info.name}"
            )
        }[args.type]

        if args.msgs_output:
            self.logger.info("Copying msg/ and srv/ from firmware.")
            self.logger.debug(f"Checking for msg/ and srv/ in {args.msgs_output}")
            msg_src = PX4_DIR / "msg"
            msg_versioned_src = PX4_DIR / "msg/versioned"
            srv_src = PX4_DIR / "srv"
            msg_dst = args.msgs_output / "msg"
            srv_dst = args.msgs_output / "srv"

            if msg_dst.exists() and msg_dst.exists():
                self.logger.debug("Found msg and srv directories. Deleting ...")
                shutil.rmtree(msg_dst)
                shutil.rmtree(srv_dst)
            else:
                self.logger.warn(f"The provided directory {args.msgs_output} does not seem to contain the folders 'msg' and 'srv'.")
                self.logger.warn(f"This may be intentional, or you may not be copying the files to the intended directory (usually to px4_msgs).")

            self.logger.debug(f"Creating empty version of msg and srv directories.")
            msg_dst.mkdir(parents=True, exist_ok=True)
            srv_dst.mkdir(parents=True, exist_ok=True)

            self.logger.debug(f"Copying *.msg and *.srv into {args.msgs_output}...")
            for file in msg_src.glob("*.msg"):
                shutil.copy(file, msg_dst)
            for file in msg_versioned_src.glob("*.msg"):
                shutil.copy(file, msg_dst)
            for file in srv_src.glob("*.srv"):
                shutil.copy(file, srv_dst)

        if not args.overwrite and (PX4_DIR / "build" / target).exists():
            self.logger.info(f"Target {target} already built. Use --overwrite to rebuild.")
            sys.exit(0)

        self.__setup_git(info)

        if args.install_dependencies:
            self.logger.info("Installing PX4 dependencies...")
            tooling = run_command(tooling_cmd, live=True, logger=self.logger, cwd=PX4_DIR)
            if tooling.returncode != 0:
                self.logger.error(f"Failed to install dependencies. {tooling.stderr}, {tooling.stdout}")
                sys.exit(1)

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
            self.logger.info(f"Make clean build")
            run_command(["make", "clean"], live=True, logger=self.logger, cwd=PX4_DIR)

        build_px4 = run_command(["make", target], live=True, logger=self.logger, cwd=PX4_DIR)

        if build_px4.returncode != 0:
            self.logger.error(f"Build failed for {target}. {build_px4.stderr} {build_px4.stdout}")
            sys.exit(1)

        if args.output and args.type == "firmware":
            output_file = args.output / f"{info.name}.px4"
            shutil.copy2(PX4_DIR / "build" / target / f"{target}.px4", output_file)
            self.logger.info(f"firmware file in: {output_file}")

        self.logger.info("Done.")


    def cleanup(self):
        self.logger.debug(f"Restoring tags.")
        self.logger.debug(f"Deleting {self.renamed_tag}")
        run_command(['git', 'tag', '-d', self.renamed_tag], cwd=PX4_DIR, check=True)

        run_command(['git', 'restore', '.'], cwd=PX4_DIR, check=True)
