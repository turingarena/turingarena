import argparse
import os

import argcomplete
from turingarena_web.cli.command import add_subparser
from turingarena_web.cli.contest import ContestCommand
from turingarena_web.cli.problem import ProblemCommand
from turingarena_web.cli.user import UserCommand

VERSION = "v0.0.1" # TODO: load version from file

PARSER = argparse.ArgumentParser()
PARSER.add_argument("--version", action="version", version=VERSION)
subparsers = PARSER.add_subparsers(dest="command", metavar="COMMAND")
subparsers.required = True
add_subparser(subparsers, UserCommand)
add_subparser(subparsers, ProblemCommand)
add_subparser(subparsers, ContestCommand)


def main():
    if argcomplete is not None:
        argcomplete.autocomplete(PARSER)

    args = PARSER.parse_args()

    # TODO: init_logger(args.log_level)

    command = args.Command(args=args, cwd=os.curdir)
    command.run()

