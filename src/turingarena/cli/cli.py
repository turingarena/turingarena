import os
from argparse import ArgumentParser

from turingarena.cli.base import BASE_PARSER
from turingarena.cli.common import init_logger
from turingarena.cli.evaluate import EvaluateCommand
from turingarena.cli.files import FileCommand
from turingarena.cli.new import NewCommand
from turingarena.cli.search import SearchCommand
from turingarena.version import VERSION

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


if __name__ == '__main__':
    main()
