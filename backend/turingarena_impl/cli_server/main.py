import json
import logging
import os
import sys
from collections import namedtuple
from tempfile import TemporaryDirectory

from turingarena_impl.cli_server.evaluate import evaluate_cmd
from turingarena_impl.cli_server.git_manager import GitManager
from turingarena_impl.cli_server.info import info_cmd
from turingarena_impl.cli_server.make import make_cmd
from turingarena_impl.cli_server.test import test_cmd
from turingarena_impl.logging import init_logger

logger = logging.getLogger(__name__)


def main():
    args = json.load(sys.stdin, object_hook=lambda d: namedtuple('X', d.keys())(*d.values()))
    do_main(args)


def do_main(args):
    init_logger(args.log_level, args.isatty)

    if args.local:
        git = GitManager(args.git_dir)
    else:
        git = GitManager("/run/turingarena/db.git")
    logger.info(f"Using git repository at {git.git_dir}")

    with TemporaryDirectory() as temp_dir:
        logger.info(f"Created temporary git working dir {temp_dir}")

        if args.repository:
            git.git_fetch_repositories(args.repository)

        if args.tree:
            git.git_import_trees(args.tree, temp_dir)

        if args.send_current_dir:
            git.git_import_trees([args.tree_id], temp_dir)

        os.chdir(temp_dir)
        if args.send_current_dir:
            os.chdir(args.current_dir)

        {
            "evaluate": evaluate_cmd,
            "make": make_cmd,
            "info": info_cmd,
            "test": test_cmd,
        }[args.command](args)
