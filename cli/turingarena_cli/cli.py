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
from functools import lru_cache

from turingarena_cli.command import Command
from turingarena_cli.common import init_logger
# in python2.7, quote is in pipes and not in shlex
from turingarena_cli.new import NewCommand
from turingarena_common.commands import EvaluateCommandParameters, WorkingDirectory, Pack
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

    @property
    @lru_cache(None)
    def git_work_dir(self):
        try:
            return subprocess.check_output(
                ["git", "rev-parse", "--show-toplevel"],
                universal_newlines=True,
            ).strip()
        except:
            working_dir = os.getcwd()
            logging.info("Initializing git repository in {}".format(working_dir))
            subprocess.call(["git", "init"])
            return working_dir

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

    def ssh_command(self):
        cli = [
            "/usr/local/bin/python",
            "-m", self.module_name,
        ]

        self.send_ssh_command(cli)

    def send_current_dir(self):
        current_dir = os.path.relpath(os.curdir, self.git_work_dir)
        logging.info("Sending work dir: {working_dir} (current dir: {current_dir})...".format(
            working_dir=self.git_work_dir,
            current_dir=current_dir,
        ))

        git_popen_args = dict(env=self.git_env, universal_newlines=True)

        subprocess.check_call(["git", "add", "-A", "."], **git_popen_args)
        logging.info("Added all files to git")

        tree_id = subprocess.check_output(["git", "write-tree"], **git_popen_args).strip()
        logging.info("Wrote tree with id {}".format(tree_id))

        if not self.args.local:
            self.do_send_current_dir(tree_id)

        return current_dir, tree_id

    def do_send_current_dir(self, tree_id):
        git_popen_args = dict(env=self.git_env, universal_newlines=True)
        logging.info("Sending current directory to the server via git")
        commit_message = "Turingarena payload."
        commit_id = subprocess.check_output(
            ["git", "commit-tree", tree_id, "-m", commit_message],
            **git_popen_args
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
        ], **git_popen_args)
        logging.info("Pushed current commit")
        # remove the remove branch (we only need the tree object)
        subprocess.check_call([
            "git", "push", "-q",
            "turingarena@localhost:db.git",
            ":refs/heads/sha-{commit_id}".format(commit_id=commit_id),
        ], **git_popen_args)

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

    def run(self):
        if not self.args.local:
            self.check_daemon()

        self.args.isatty = sys.stderr.isatty()
        self.args.git_dir = self.git_dir

        if self.args.repository is None:
            self.args.send_current_dir = True

        if self.args.command not in ["evaluate", "make", "test"]:
            self.args.send_current_dir = False

        if self.args.send_current_dir:
            self.args.current_dir, self.args.tree_id = self.send_current_dir()

        self.args.result_file = os.path.join("/tmp", "turingarena_{}_result.json".format(str(uuid.uuid4())))

        if self.args.local:
            self.local_command()
        else:
            self.ssh_command()

        if self.args.command == "make" and not self.args.print:
            self.retrieve_result(self.args.result_file)


class DaemonCommand(AbstractDaemonCommand):
    def _get_module_name(self):
        return "turingarena_impl.cli_server.runner"


class EvaluateCommand(DaemonCommand):
    def _get_parameters(self):
        return EvaluateCommandParameters(
            working_directory=build_working_directory(self.args),
            evaluator=self.args.evaluator,
        )


class LegacyDaemonCommand(AbstractDaemonCommand):
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

        return super().run()


def build_working_directory(args):
    return WorkingDirectory(
        pack=Pack(
            parts=[args.tree_id],
            repositories=[],
        ),
        current_directory=args.current_dir,
    )


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

    command = args.Command(args)
    command.run()
