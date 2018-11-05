import os

from argparse import ArgumentParser

from .common import init_logger
from .search import SearchCommand
from .submit import SubmitCommand
from .login import LoginCommand
from .get import GetCommand

# PYTHON_ARGCOMPLETE_OK
try:
    import argcomplete
except ImportError:
    argcomplete = None

PARSER = ArgumentParser()

subparsers = PARSER.add_subparsers(dest="command", metavar="COMMAND")
subparsers.required = True


subparsers.add_parser(
    "search",
    parents=[SearchCommand.PARSER],
    help=SearchCommand.PARSER.description,
).set_defaults(Command=SearchCommand)
subparsers.add_parser(
    "get",
    parents=[GetCommand.PARSER],
    help=GetCommand.PARSER.description,
).set_defaults(Command=GetCommand)
subparsers.add_parser(
    "submit",
    parents=[SubmitCommand.PARSER],
    help=SubmitCommand.PARSER.description,
).set_defaults(Command=SubmitCommand)
subparsers.add_parser(
    "login",
    parents=[LoginCommand.PARSER],
    help=LoginCommand.PARSER.description,
).set_defaults(Command=LoginCommand)


def main():
    if argcomplete is not None:
        argcomplete.autocomplete(PARSER)

    args = PARSER.parse_args()

    init_logger(args.log_level)

    command = args.Command(args=args, cwd=os.curdir)
    command.run()


if __name__ == '__main__':
    main()
