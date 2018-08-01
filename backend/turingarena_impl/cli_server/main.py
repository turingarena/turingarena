import logging
import json
import sys

from turingarena_impl.cli_server.evaluate import evaluate_cmd
from turingarena_impl.cli_server.git_manager import setup_git_environment, git_fetch_repositories, git_import_trees, \
    receive_current_directory
from turingarena_impl.cli_server.info import info_cmd
from turingarena_impl.cli_server.make import make_cmd
from turingarena_impl.logging import init_logger


logger = logging.getLogger(__name__)


def main():
    args = json.loads(sys.argv[1])

    init_logger(args["log_level"])

    with setup_git_environment(local=args["local"], git_dir=args["git_dir"]):

        if args["send_current_dir"]:
            receive_current_directory(args["current_dir"], args["tree_id"])

        if args["repository"]:
            git_fetch_repositories(args["repository"])

        if args["tree"]:
            git_import_trees(args["tree"])

        if args["command"] == "evaluate":
            evaluate_cmd(args["file"], args["evaluator"], args["raw"])

        if args["command"] == "make":
            make_cmd(args)

        if args["command"] == "info":
            info_cmd(args["what"])


if __name__ == "__main__":
    main()
