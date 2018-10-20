import os
from argparse import ArgumentParser

from turingarena_cli.cloud import CloudCommand
from turingarena_cli.common import init_logger
from turingarena_cli.daemonctl import DAEMON_CONTROL_PARSER
from turingarena_cli.evaluate import EvaluateCommand
from turingarena_cli.files import FileCommand
from turingarena_cli.info import InfoCommand
from turingarena_cli.make import LegacyMakeCommand, LegacyTemplateCommand, LegacySkeletonCommand
from turingarena_cli.new import NewCommand
from turingarena_cli.remote import RemoteExecCommand

# in python2.7, quote is in pipes and not in shlex
from turingarena_cli.test import TestCommand

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
    parents=[EvaluateCommand.PARSER],
    help=EvaluateCommand.PARSER.description,
)
subparsers.add_parser(
    "info",
    parents=[InfoCommand.PARSER],
    help=InfoCommand.PARSER.description,
)
subparsers.add_parser(
    "test",
    parents=[TestCommand.PARSER],
    help=TestCommand.PARSER.description,
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
    "make",
    parents=[LegacyMakeCommand.PARSER],
    help=LegacyMakeCommand.PARSER.description,
)
subparsers.add_parser(
    "skeleton",
    parents=[LegacySkeletonCommand.PARSER],
    help="generate skeleton",
)
subparsers.add_parser(
    "template",
    parents=[LegacyTemplateCommand.PARSER],
    help="generate template",
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


def main():
    if argcomplete is not None:
        argcomplete.autocomplete(PARSER)

    args = PARSER.parse_args()

    init_logger(args.log_level)

    command = args.Command(args=args, cwd=os.curdir)
    command.run()
