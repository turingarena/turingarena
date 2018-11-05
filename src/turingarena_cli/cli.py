import os
from argparse import ArgumentParser

from turingarena_cli.cloud import CloudCommand
from turingarena_cli.common import init_logger
from turingarena_cli.daemonctl import DAEMON_CONTROL_PARSER
from turingarena_cli.evaluate import RemoteEvaluateCommand
from turingarena_cli.files import FileCommand
from turingarena_cli.info import InfoCommand
from turingarena_cli.new import NewCommand
from turingarena_cli.remote import RemoteExecCommand
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

subparsers = PARSER.add_subparsers(dest="command", metavar="COMMAND")
subparsers.required = True

subparsers.add_parser(
    "evaluate",
    parents=[RemoteEvaluateCommand.PARSER],
    help=RemoteEvaluateCommand.PARSER.description,
)
subparsers.add_parser(
    "info",
    parents=[InfoCommand.PARSER],
    help=InfoCommand.PARSER.description,
)
subparsers.add_parser(
    "new",
    parents=[NewCommand.PARSER],
    help=NewCommand.PARSER.description,
)
subparsers.add_parser(
    "file",
    parents=[FileCommand.PARSER],
    help=FileCommand.PARSER.description,
)
subparsers.add_parser(
    "daemon",
    parents=[DAEMON_CONTROL_PARSER],
    help=DAEMON_CONTROL_PARSER.description,
)
subparsers.add_parser(
    "exec",
    parents=[RemoteExecCommand.PARSER],
    help=RemoteExecCommand.PARSER.description,
).set_defaults(Command=RemoteExecCommand)
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
