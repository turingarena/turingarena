import argparse
import importlib
import logging
import os
import pickle
import subprocess
import sys
from abc import abstractmethod
from argparse import ArgumentParser
from functools import lru_cache

from turingarena_cli.base import BASE_PARSER
from turingarena_cli.command import Command
from turingarena_common.commands import LocalExecutionParameters, RemoteCommandParameters

# in python2.7, quote is in pipes and not in shlex
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


class RemoteCommand(Command):
    def check_daemon(self):
        cli = SSH_BASE_CLI + [SSH_USER, "echo", "OK!"]
        try:
            subprocess.check_output(cli)
        except subprocess.CalledProcessError:
            sys.exit("turingarenad is not running! Run it with `sudo turingarenad --daemon`")

    @abstractmethod
    def _get_remote_cli(self):
        pass

    def _on_send_stdin(self, stdin):
        pass

    def run(self):
        self.check_daemon()
        cli = SSH_BASE_CLI + [
            "turingarena@localhost",
        ] + [quote(c) for c in self._get_remote_cli()]

        logging.info("Sending command to the server via ssh")
        logging.debug(cli)

        p = subprocess.Popen(cli, stdin=subprocess.PIPE)
        self._on_send_stdin(p.stdin)
        p.stdin.close()
        p.wait()

    PARSER = ArgumentParser(add_help=False, parents=[BASE_PARSER])
    PARSER.add_argument(
        "--local", "-l",
        action="store_true",
        help="execute turingarena locally (do not connect to docker)",
    )


class AbstractRemotePythonCommand(RemoteCommand):
    def _run_locally(self):
        module = importlib.import_module(self.module_name)
        module.do_main(self.parameters)

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

    def _get_remote_cli(self):
        return [
            "/usr/local/bin/python",
            "-m", self.module_name,
        ]

    def _on_send_stdin(self, stdin):
        pickle.dump(self.parameters, stdin)

    @property
    @lru_cache(None)
    def git_dir(self):
        return os.path.join(os.path.expanduser("~"), ".turingarena", "db.git")

    def run(self):
        self.args.isatty = sys.stderr.isatty()
        if self.args.local:
            self._run_locally()
        else:
            super().run()


class RemotePythonCommand(AbstractRemotePythonCommand):
    def _get_parameters(self):
        if self.args.local:
            local_execution = LocalExecutionParameters(
                git_dir=self.git_dir,
            )
        else:
            local_execution = None

        return RemoteCommandParameters(
            log_level=self.args.log_level,
            stderr_isatty=sys.stderr.isatty(),
            local_execution=local_execution,
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


class RemoteExecCommand(RemoteCommand):
    PARSER = ArgumentParser(
        description="Execute an arbitrary command on the daemon (for testing)",
        add_help=False,
        parents=[RemoteCommand.PARSER],
    )
    PARSER.add_argument("cli", nargs=argparse.REMAINDER)

    def _get_remote_cli(self):
        return self.args.cli
