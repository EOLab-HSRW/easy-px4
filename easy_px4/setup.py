import os
import sys
import subprocess
from setuptools import setup, find_packages
from setuptools.command.install import install
from setuptools.command.develop import develop
from pathlib import Path

if not sys.platform.startswith("linux"):
    sys.stderr.write("This package is deliberately restricted to GNU/Linux systems.")
    sys.exit(1)

__package__ = "easy_px4"

with (Path(__file__).resolve().parent / "README.md").open(encoding='utf-8') as f:
    long_description = f.read()

def common_install() -> None:
    env_work_dir = os.environ.get("EASY_PX4_WORK_DIR", str(Path.home()))
    install_deps = os.environ.get("EASY_PX4_INSTALL_DEPS", "true")
    clone_px4 = os.environ.get("EASY_PX4_CLONE_PX4", "true")

    WORK_DIR = Path(env_work_dir) / f".{__package__}"
    WORK_DIR.mkdir(exist_ok=True)

    PX4_DIR = WORK_DIR / "PX4-Autopilot"

    if not PX4_DIR.exists():
        try:
            if clone_px4 == "true":
                git_clone = subprocess.run(
                    ["git", "clone", "https://github.com/PX4/PX4-Autopilot", "--recursive", "--no-tags"],
                    cwd=WORK_DIR,
                    check=True,
                    stdout=sys.stdout,
                    stderr=sys.stderr, 
                    text=True
                )

                if git_clone.returncode != 0:
                    sys.stderr.write(git_clone.stdout)
                    sys.stderr.write(git_clone.stderr)
                    sys.exit(1)

            if install_deps == "true":
                install_dependencies = subprocess.run(
                    ["./Tools/setup/ubuntu.sh"],
                    cwd=PX4_DIR,
                    check=True,
                    stdout=sys.stdout,
                    stderr=sys.stderr, 
                    text=True
                )

                if install_dependencies.returncode != 0:
                    sys.stderr.write(install_dependencies.stdout)
                    sys.stderr.write(install_dependencies.stderr)
                    sys.exit(1)
        except subprocess.CalledProcessError as e:
            print("Failed to setup PX4-Autopilot repository.")
            print("stdout:", e.stdout)
            print("stderr:", e.stderr)
            sys.exit(1)


class InstallCommand(install):

    def run(self):
        common_install()
        return super().run()

class DevelopCommand(develop):

    def run(self):
        common_install()
        return super().run()

dev_minimal = [
    "pytest",
    "mypy"
]

setup(
    name=__package__,
    version='0.0.1',
    url='https://github.com/EOLab-HSRW/easy-px4.git',
    author='Harley Lara',
    author_email='harley.lara@outlook.com',
    description='A helper tool to build custom PX4 firmwares',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    python_requires='>=3.9',
    install_requires=[
        'tomli',
        'easy_px4_utils',
    ],
    extras_require={
        "test": dev_minimal,
        "dev": dev_minimal
    },
    cmdclass={
        'install': InstallCommand,
        'develop': DevelopCommand,
    },
    entry_points={
        "console_scripts": [
            f"{__package__} = {__package__}.__main:main",
        ],
    },
)
