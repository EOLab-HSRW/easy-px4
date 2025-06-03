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


    WORK_DIR = Path().home() / f".{__package__}"
    WORK_DIR.mkdir(exist_ok=True)

    PX4_DIR = WORK_DIR / "PX4-Autopilot"

    if not PX4_DIR.exists():
        try:
            px4_clone = subprocess.run(
                ["git", "clone", "https://github.com/PX4/PX4-Autopilot", "--recursive"],
                cwd=WORK_DIR,
                check=True,
                stdout=sys.stdout,
                stderr=sys.stderr,
                text=True
            )
        except subprocess.CalledProcessError as e:
            print("Failed to clone repository.")
            print("stdout:", e.stdout)
            print("stderr:", e.stderr)


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
    description='A helper tool to build custom PX4 firmware',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    python_requires='>=3.10',
    install_requires=[
        'tomli',
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
            f"{__package__} = {__package__}.main:main",
        ],
    },
)
