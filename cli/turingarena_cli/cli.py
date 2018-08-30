from __future__ import print_function

import argparse
import os

from turingarena_cli.common import init_logger
# in python2.7, quote is in pipes and not in shlex
from turingarena_cli.evaluate import create_evaluate_parser
from turingarena_cli.files import create_file_parser
from turingarena_cli.legacy import create_info_parser, create_make_parser, create_test_parser
from turingarena_cli.new import create_new_parser
from turingarena_cli.pack import PACK_COMMAND_PARSER
from turingarena_cli.remote import REMOTE_COMMAND_PARSER

try:
    from shlex import quote
except ImportError:
    from pipes import quote


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Turingarena CLI",
        parents=[PACK_COMMAND_PARSER, REMOTE_COMMAND_PARSER],
    )
    parser.add_argument("--log-level", help="log level", default="WARNING")

    subparsers = parser.add_subparsers(title="command", dest="command")
    subparsers.required = True

    create_evaluate_parser(subparsers)
    create_info_parser(subparsers)
    create_new_parser(subparsers)
    create_test_parser(subparsers)
    create_file_parser(subparsers)

    make_parser = subparsers.add_parser("make", help="Generate all the necessary files for a problem")
    create_make_parser(make_parser)
    skeleton_parser = subparsers.add_parser("skeleton", help="generate skeleton")
    create_make_parser(skeleton_parser, alias=True)
    template_parser = subparsers.add_parser("template", help="generate template")
    create_make_parser(template_parser, alias=True)

    return parser.parse_args()


def main():
    args = parse_arguments()

    init_logger(args.log_level)

    command = args.Command(args=args, cwd=os.curdir)
    command.run()
