import logging
import json

from collections import namedtuple

from turingarena_impl.cli_server.evaluate import evaluate_cmd
from turingarena_impl.cli_server.git_manager import setup_git_environment, git_fetch_repositories, git_import_trees, \
    receive_current_directory
from turingarena_impl.cli_server.info import info_cmd
from turingarena_impl.cli_server.make import make_cmd
from turingarena_impl.cli_server.test import test_cmd
from turingarena_impl.logging import init_logger


logger = logging.getLogger(__name__)


def json_to_object(json_data):
    return json.loads(json_data, object_hook=lambda d: namedtuple('X', d.keys())(*d.values()))


def main(json_args):
    args = json_to_object(json_args)

    init_logger(args.log_level)

    with setup_git_environment(local=args.local, git_dir=args.git_dir):

        if args.send_current_dir:
            receive_current_directory(args.current_dir, args.tree_id)

        if args.repository:
            git_fetch_repositories(args.repository)

        if args.tree:
            git_import_trees(args.tree)

        {
            "evaluate": evaluate_cmd,
            "make": make_cmd,
            "info": info_cmd,
            "test": test_cmd,
        }[args.command](args)
