from __future__ import print_function

import argparse
import importlib
import json
import logging
import os
import pickle
import subprocess
import sys
import uuid
from abc import abstractmethod
from argparse import ArgumentParser
from contextlib import contextmanager
from functools import lru_cache
from tempfile import TemporaryDirectory

from turingarena_cli.command import Command
from turingarena_cli.common import init_logger
# in python2.7, quote is in pipes and not in shlex
from turingarena_cli.new import NewCommand
from turingarena_common.commands import EvaluateCommandParameters, WorkingDirectory, Pack, GitCloneRepository, \
    DaemonCommandParameters
from turingarena_common.git_common import GIT_BASE_ENV

try:
    from shlex import quote
except ImportError:
    from pipes import quote

SSH_BASE_CLI = [
    "ssh",
    "-T",
    "-o", "BatchMode=yes",
    "-o", "LogLevel=error",
    "-o", "UserKnownHostsFile=/dev/null",
    "-o", "StrictHostKeyChecking=no",
    "-p", "20122", "-q",
]
SSH_USER = "turingarena@localhost"

PACK_COMMAND_PARSER = ArgumentParser(add_help=False)

PACK_COMMAND_PARSER.add_argument(
    "--send-current-dir", "-s",
    action="store_true",
    help="send the current directory",
)
PACK_COMMAND_PARSER.add_argument(
    "--tree", "-t",
    action="append",
    help="a git tree id",
)
PACK_COMMAND_PARSER.add_argument(
    "--repository", "-r",
    action="append",
    help="source of a git repository",
)

DAEMON_COMMAND_PARSER = ArgumentParser(add_help=False)
DAEMON_COMMAND_PARSER.add_argument(
    "--local", "-l",
    action="store_true",
    help="execute turingarena locally (do not connect to docker)",
)


class AbstractDaemonCommand(Command):
    def check_daemon(self):
        cli = SSH_BASE_CLI + [SSH_USER, "echo", "OK!"]
        try:
            subprocess.check_output(cli)
        except subprocess.CalledProcessError:
            sys.exit("turingarenad is not running! Run it with `sudo turingarenad --daemon`")

    def local_command(self):
        module = importlib.import_module(self.module_name)
        module.do_main(self.parameters)

    def send_ssh_command(self, cli):
        cli = SSH_BASE_CLI + [
            "turingarena@localhost",
        ] + cli

        logging.info("Sending command to the server via ssh")
        logging.debug(cli)

        p = subprocess.Popen(cli, stdin=subprocess.PIPE)
        pickle.dump(self.parameters, p.stdin)
        p.stdin.close()
        p.wait()

    @property
    def module_name(self):
        return self._get_module_name()

    @property
    def parameters(self):
        return self._get_parameters()

    @abstractmethod
    def _get_module_name(self):
        pass

    @abstractmethod
    def _get_parameters(self):
        pass

    def ssh_command(self):
        cli = [
            "/usr/local/bin/python",
            "-m", self.module_name,
        ]

        self.send_ssh_command(cli)

    def run(self):
        if not self.args.local:
            self.check_daemon()

        self.args.isatty = sys.stderr.isatty()
        if self.args.local:
            self.local_command()
        else:
            self.ssh_command()


class DaemonCommand(AbstractDaemonCommand):
    def _get_parameters(self):
        return DaemonCommandParameters(
            log_level=self.args.log_level,
            stderr_isatty=sys.stderr.isatty(),
            command=self.command_parameters,
        )

    @property
    @lru_cache(None)
    def command_parameters(self):
        return self._get_command_parameters()

    @abstractmethod
    def _get_command_parameters(self):
        pass

    def _get_module_name(self):
        return "turingarena_impl.cli_server.runner"


class PackBasedCommand(AbstractDaemonCommand):
    @property
    @lru_cache(None)
    def git_work_dir(self):
        try:
            work_dir = subprocess.check_output(
                ["git", "rev-parse", "--show-toplevel"],
                universal_newlines=True,
            ).strip()
        except:
            work_dir = self.cwd
            logging.info("Initializing git repository in {}".format(work_dir))
            subprocess.call(["git", "init"])
        logging.info("Work dir: {work_dir}".format(work_dir=work_dir))
        return work_dir

    @property
    @lru_cache(None)
    def git_dir(self):
        return os.path.join(os.path.expanduser("~"), ".turingarena", "db.git")

    @property
    def git_env(self):
        git_env = {
            "GIT_WORK_TREE": self.git_work_dir,
            "GIT_DIR": self.git_dir,
            "GIT_SSH_COMMAND": " ".join("'" + c + "'" for c in SSH_BASE_CLI),
        }
        git_env.update(GIT_BASE_ENV)
        return git_env

    def git_init(self):
        subprocess.check_call(["git", "init", "--quiet", "--bare", self.git_dir])
        logging.info("Initialized git repository in {}".format(self.git_dir))

    @contextmanager
    def _temp_git_index(self):
        with TemporaryDirectory() as temp_dir:
            env = {}
            env.update(self.git_env)
            env.update({
                "GIT_INDEX_FILE": os.path.join(temp_dir, "index")
            })
            yield env

    @property
    @lru_cache(None)
    def local_tree_id(self):
        logging.info("Packing local tree")
        with self._temp_git_index() as env:
            subprocess.check_call(["git", "add", "-A", "."], env=env)
            logging.info("Added all files to git")

            tree_id = subprocess.check_output(
                ["git", "write-tree"],
                env=env,
                universal_newlines=True,
            ).strip()
            logging.info("Wrote tree with id {}".format(tree_id))
            return tree_id

    @property
    @lru_cache(None)
    def relative_current_dir(self):
        current_dir = os.path.relpath(self.cwd, self.git_work_dir)
        logging.info("Relative current dir: {current_dir}".format(current_dir=current_dir))
        return current_dir

    def push_local_tree(self, tree_id):
        logging.info("Sending current directory to the server via git")
        commit_message = "Turingarena payload."

        commit_id = subprocess.check_output(
            ["git", "commit-tree", tree_id, "-m", commit_message],
            env=self.git_env,
            universal_newlines=True,
        ).strip()
        logging.info("Created commit {}".format(commit_id))

        subprocess.check_call(SSH_BASE_CLI + [
            "turingarena@localhost",
            "git init --bare --quiet db.git",
        ])
        logging.info("Initialized git repository on the server")

        subprocess.check_call([
            "git", "push", "-q",
            "turingarena@localhost:db.git",
            "{commit_id}:refs/heads/sha-{commit_id}".format(commit_id=commit_id),
        ], env=self.git_env)
        logging.info("Pushed current commit")

        # remove the remove branch (we only need the tree object)
        subprocess.check_call([
            "git", "push", "-q",
            "turingarena@localhost:db.git",
            ":refs/heads/sha-{commit_id}".format(commit_id=commit_id),
        ], env=self.git_env)

    def retrieve_result(self, result_file):
        logging.info("Retrieving result")
        logging.info("Reading {}".format(result_file))
        with open(result_file) as f:
            result = f.read().strip()

        logging.info("Got {}".format(result))
        result = json.loads(result)

        tree_id = result["tree_id"]
        commit_it = result["commit_id"]

        logging.info("Importing tree id {}".format(tree_id))
        subprocess.call(["git", "read-tree", tree_id], env=self.git_env)
        logging.info("Checking out")
        subprocess.call(["git", "checkout-index", "--all", "-q"], env=self.git_env)

    @property
    def working_directory(self):
        parts = []
        if self.args.send_current_dir:
            parts += [self.local_tree_id]

        return WorkingDirectory(
            pack=Pack(
                parts=parts,
                repositories=[
                    GitCloneRepository(
                        url=url,
                        branch=None,
                        depth=None,
                    )
                    for url in self.args.repository or []
                ],
            ),
            current_directory=self.relative_current_dir,
        )


class EvaluateCommand(DaemonCommand, PackBasedCommand):
    def _get_command_parameters(self):
        return EvaluateCommandParameters(
            working_directory=self.working_directory,
            evaluator=self.args.evaluator,
            file=self.args.file,
            raw_output=self.args.raw,
        )


class LegacyDaemonCommand(PackBasedCommand):
    def _get_module_name(self):
        return "turingarena_impl.cli_server.main"

    def _get_parameters(self):
        return self.args

    def run(self):
        if self.args.command in ["skeleton", "template"]:
            self.args.what = self.args.command
            self.args.command = "make"

        if self.args.command == "make" and self.args.what != "all":
            self.args.print = True

        self.args.git_dir = self.git_dir

        if self.args.repository is None:
            self.args.send_current_dir = True

        if self.args.command not in ["evaluate", "make", "test"]:
            self.args.send_current_dir = False

        if self.args.send_current_dir:
            if not self.args.local:
                self.push_local_tree(self.local_tree_id)
            self.args.tree_id = self.local_tree_id
            self.args.current_dir = self.relative_current_dir
        else:
            self.args.tree_id = None
            self.args.current_dir = None

        self.args.result_file = os.path.join("/tmp", "turingarena_{}_result.json".format(str(uuid.uuid4())))

        super().run()

        if self.args.command == "make" and not self.args.print:
            self.retrieve_result(self.args.result_file)


def create_evaluate_parser(subparsers):
    parser = subparsers.add_parser("evaluate", help="Evaluate a submission")
    parser.add_argument("file", help="submission file", nargs="+")
    parser.add_argument("--evaluator", "-e", help="evaluator program", default="evaluator.py")
    parser.add_argument("--raw", "-r", help="use raw output", action="store_true")

    parser.set_defaults(Command=EvaluateCommand)


def create_make_parser(parser, alias=False):
    if not alias:
        parser.add_argument("what", help="what to make", default="all",
                            choices=["all", "skeleton", "template", "metadata", "description"])
    parser.add_argument("--language", "-l", help="which language to generate", action="append",
                        choices=["python", "c++", "java", "go"])
    parser.add_argument("--print", "-p", help="Print output to stdout instead of writing it to a file",
                        action="store_true")
    parser.set_defaults(Command=LegacyDaemonCommand)


def create_new_parser(subparsers):
    parser = subparsers.add_parser("new", help="Create a new Turingarena problem")
    parser.add_argument("name", help="problem name")
    parser.set_defaults(Command=NewCommand)


def create_info_parser(subparsers):
    parser = subparsers.add_parser("info", help="get some info about TuringArena")
    parser.add_argument("what", choices=["languages"], help="what you want to know about turingarena")
    parser.set_defaults(Command=LegacyDaemonCommand)


def create_test_parser(subparsers):
    parser = subparsers.add_parser("test", help="execute tests")
    parser.add_argument("pytest_arguments", nargs="*", help="additional arguments to pass to pytest")
    parser.set_defaults(Command=LegacyDaemonCommand)


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Turingarena CLI",
        parents=[PACK_COMMAND_PARSER, DAEMON_COMMAND_PARSER],
    )
    parser.add_argument("--log-level", help="log level", default="WARNING")

    subparsers = parser.add_subparsers(title="command", dest="command")
    subparsers.required = True

    create_evaluate_parser(subparsers)
    create_info_parser(subparsers)
    create_new_parser(subparsers)
    create_test_parser(subparsers)

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
