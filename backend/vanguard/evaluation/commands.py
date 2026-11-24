"""The registry of evaluation subcommands.

A command module calls register() at import time; vanguard.evaluation.__main__ imports
every command module listed in MODULES, so each command appears in the parser.
"""

import argparse
from collections.abc import Callable
from dataclasses import dataclass


@dataclass(frozen=True)
class Command:
    name: str
    help: str
    add_arguments: Callable[[argparse.ArgumentParser], None]
    run: Callable[[argparse.Namespace], int]


COMMANDS: dict[str, Command] = {}

# Modules that define commands, imported by the command line. Later steps add to it.
MODULES: list[str] = ["vanguard.evaluation.tasks"]


def register(command: Command) -> Command:
    if command.name in COMMANDS:
        raise ValueError(f"evaluation command {command.name!r} is defined twice")
    COMMANDS[command.name] = command
    return command
