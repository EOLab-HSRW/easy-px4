import sys
import argparse

from .commands.command import Command
from .commands.build import BuildCommand

# available command registration
COMMAND_REGISTRY: list[type[Command]] = [
    BuildCommand
]


def main():
    """
    Main entrypoint for the CLI tool.

    Commands exposed to the cli must be part of the COMMAND_REGISTRY.


    We map from the `cmd_name` to the implementation so that the cli
    knows which command to execute based on the command received as an argument.
    """

    parser = argparse.ArgumentParser(
        prog=__package__,
        description="A simple tool to help building custom PX4-firmwares"
    )

    subparsers = parser.add_subparsers(dest="command", required=True, help="Available commands")

    cmd_register = {}

    for command_class in COMMAND_REGISTRY:
        subparser = subparsers.add_parser(command_class.cmd_name, help=f"{command_class.cmd_name} command")
        command_class().add_arguments(subparser)
        cmd_register[command_class.cmd_name] = command_class

    args = parser.parse_args()

    with cmd_register[args.command]() as worker:
        worker.execute(args)

    return 0


if __name__ == "__main__":
    sys.exit(main())
