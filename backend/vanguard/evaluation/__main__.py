"""Command line for the evaluation package: python -m vanguard.evaluation <command>."""

import argparse
import importlib

from vanguard.evaluation.commands import COMMANDS, MODULES


def build_parser() -> argparse.ArgumentParser:
    for module in MODULES:
        importlib.import_module(module)
    parser = argparse.ArgumentParser(
        prog="python -m vanguard.evaluation",
        description="Task-level evaluation of stored Vanguard runs.",
    )
    sub = parser.add_subparsers(dest="command", metavar="<command>")
    for name, command in sorted(COMMANDS.items()):
        command.add_arguments(sub.add_parser(name, help=command.help, description=command.help))
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command is None:
        parser.print_help()
        return 1
    return COMMANDS[args.command].run(args)


if __name__ == "__main__":
    raise SystemExit(main())
