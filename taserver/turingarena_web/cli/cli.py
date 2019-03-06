import argparse

# PYTHON_ARGCOMPLETE_OK
try:
    import argcomplete
except ImportError:
    argcomplete = None

from turingarena_web import init_logger
from turingarena_web.cli.command import add_subparser
from turingarena_web.cli.contest import ContestCommand
from turingarena_web.cli.user import UserCommand
from turingarena_web.cli.server import ServerCommand

VERSION = "v0.0.1"  # TODO: load version from file

PARSER = argparse.ArgumentParser()
PARSER.add_argument("--version", action="version", version=VERSION)
subparsers = PARSER.add_subparsers(dest="command", metavar="COMMAND")
subparsers.required = True
add_subparser(subparsers, UserCommand)
add_subparser(subparsers, ContestCommand)
add_subparser(subparsers, ServerCommand)


def main():
    if argcomplete is not None:
        argcomplete.autocomplete(PARSER)

    args = PARSER.parse_args()

    init_logger(args.log_level, isatty=True)

    command = args.Command(args=args)
    command.run()
