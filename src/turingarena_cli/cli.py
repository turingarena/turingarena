import os
from argparse import ArgumentParser

try:
    from turingarena_cli.version import VERSION
except ImportError:
    VERSION = "UNKNOWN"

from turingarena_cli.base import BASE_PARSER
from turingarena_cli.cloud import CloudCommand
from turingarena_cli.common import init_logger
from turingarena_cli.evaluate import EvaluateCommand
from turingarena_cli.files import FileCommand
from turingarena_cli.new import NewCommand
# in python2.7, quote is in pipes and not in shlex
from turingarena_cli.search import SearchCommand

try:
    from shlex import quote
except ImportError:
    from pipes import quote

# PYTHON_ARGCOMPLETE_OK
try:
    import argcomplete
except ImportError:
    argcomplete = None

PARSER = ArgumentParser()
PARSER.add_argument("--version", action="version", version=VERSION)

subparsers = PARSER.add_subparsers(dest="command", metavar="COMMAND")
subparsers.required = True

subparsers.add_parser(
    "evaluate",
    parents=[EvaluateCommand.PARSER, BASE_PARSER],
    help=EvaluateCommand.PARSER.description,
)
subparsers.add_parser(
    "new",
    parents=[NewCommand.PARSER],
    help=NewCommand.PARSER.description,
)
subparsers.add_parser(
    "file",
    parents=[FileCommand.PARSER, BASE_PARSER],
    help=FileCommand.PARSER.description,
)
subparsers.add_parser(
    "cloud",
    parents=[CloudCommand.PARSER],
    help=CloudCommand.PARSER.description,
)
subparsers.add_parser(
    "search",
    parents=[SearchCommand.PARSER],
    help=SearchCommand.PARSER.description,
).set_defaults(Command=SearchCommand)


def main():
    if argcomplete is not None:
        argcomplete.autocomplete(PARSER)

    args = PARSER.parse_args()

    init_logger(args.log_level)

    command = args.Command(args=args, cwd=os.curdir)
    command.run()
