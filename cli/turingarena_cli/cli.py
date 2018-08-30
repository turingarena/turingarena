from __future__ import print_function

import argparse
import os

from turingarena_cli.common import init_logger
from turingarena_cli.daemonctl import DaemonControlCommand
from turingarena_cli.evaluate import EvaluateCommand
from turingarena_cli.files import FileCommand
from turingarena_cli.legacy import INFO_PARSER, TEST_PARSER, BASE_MAKE_PARSER, MAKE_PARSER
from turingarena_cli.new import NewCommand

# in python2.7, quote is in pipes and not in shlex
try:
    from shlex import quote
except ImportError:
    from pipes import quote

# PYTHON_ARGCOMPLETE_OK
try:
    import argcomplete
except ImportError:
    pass

PARSER = argparse.ArgumentParser(description="Turingarena CLI")
LOG_LEVELS = ["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", ]
PARSER.add_argument(
    "--log-level",
    help="log level ({})".format(",".join(LOG_LEVELS)),
    type=str.upper,
    metavar="LEVEL",
    choices=LOG_LEVELS,
    default="WARNING",
)

subparsers = PARSER.add_subparsers(dest="command", metavar="COMMAND")
subparsers.required = True

subparsers.add_parser("evaluate", parents=[EvaluateCommand.PARSER], help=EvaluateCommand.PARSER.description)
subparsers.add_parser("info", parents=[INFO_PARSER], help=INFO_PARSER.description)
subparsers.add_parser("test", parents=[TEST_PARSER], help=TEST_PARSER.description)
subparsers.add_parser("new", parents=[NewCommand.PARSER], help=NewCommand.PARSER.description)
subparsers.add_parser("file", parents=[FileCommand.PARSER], help=FileCommand.PARSER.description)
subparsers.add_parser("make", parents=[MAKE_PARSER], help=MAKE_PARSER.description)
subparsers.add_parser("skeleton", parents=[BASE_MAKE_PARSER], help="generate skeleton")
subparsers.add_parser("template", parents=[BASE_MAKE_PARSER], help="generate template")
subparsers.add_parser("daemon", parents=[DaemonControlCommand.PARSER], help=DaemonControlCommand.PARSER.description)


def main():
    try:
        argcomplete.autocomplete(PARSER)
    except NameError:
        pass
    args = PARSER.parse_args()

    init_logger(args.log_level)

    command = args.Command(args=args, cwd=os.curdir)
    command.run()
