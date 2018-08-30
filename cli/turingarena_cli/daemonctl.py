import logging
import os
import subprocess
import sys
from argparse import ArgumentParser

from turingarena_cli.base import BASE_PARSER
from turingarena_cli.command import Command


class DaemonControlCommand(Command):
    PARSER = ArgumentParser(add_help=False, parents=[BASE_PARSER])
    PARSER.add_argument(
        "--container-name",
        help="name of the container to run",
    )
    PARSER.add_argument(
        "--sudo",
        action="store_true",
        help="use sudo to run docker",
    )

    @property
    def use_sudo(self):
        return bool(self.args.sudo)

    @property
    def image(self):
        return "turingarena/turingarena:latest"

    @property
    def container_name(self):
        return self.args.container_name or "turingarena"


class DaemonStartCommand(DaemonControlCommand):
    PARSER = ArgumentParser(
        description="Start the daemon",
        add_help=False,
        parents=[DaemonControlCommand.PARSER],
    )
    PARSER.add_argument(
        "--dev-dir",
        help="source code directory of TuringArena (for development)",
    )
    PARSER.add_argument(
        "--detach",
        action="store_true",
        help="Detach from daemon",
    )

    @property
    def detach(self):
        return bool(self.args.detach)

    def run(self):
        volumes = []
        if self.args.dev_dir:
            dev_dir = os.path.abspath(self.args.dev_dir)
            logging.info("Developement mode: mounting {} into the container".format(dev_dir))
            volumes.append("--mount=type=bind,src={},dst=/usr/local/turingarena/,readonly".format(dev_dir))

        cli = []
        if self.use_sudo:
            cli += ["sudo"]
        cli += [
            "docker",
            "run",
            "--name={}".format(self.container_name),
            "--rm",
        ]
        if self.detach:
            cli += ["--detach"]
        cli += [
            "--read-only",
            "--tmpfs=/run/turingarena:exec,mode=1777,uid=1000",
            "--tmpfs=/tmp:exec,mode=1777",
        ]
        cli += volumes
        cli += [
            "--publish=127.0.0.1:20122:22",
            self.image,
            "socat",
            "TCP-LISTEN:22,fork",
            """EXEC:"/usr/sbin/sshd -q -i -e -o PermitEmptyPasswords=yes -o Protocol=2",nofork""",
        ]

        cli_line = " ".join(cli)
        logging.info("Running: {}".format(cli_line))
        print(cli_line, file=sys.stderr)
        p = subprocess.Popen(cli, cwd="/")
        p.wait()
        if self.detach and p.returncode == 0:
            print("Turingarena is running in background, use `turingarena daemon stop` to terminate it",
                  file=sys.stderr)


class DaemonStopCommand(DaemonControlCommand):
    PARSER = ArgumentParser(
        description="Stop the daemon",
        add_help=False,
        parents=[DaemonControlCommand.PARSER],
    )

    def run(self):
        logging.info("Killing turingarena daemon")
        cli = []
        if self.use_sudo:
            cli += ["sudo"]
        cli += ["docker", "kill", self.container_name]
        p = subprocess.Popen(cli)
        p.wait()


DAEMON_CONTROL_PARSER = ArgumentParser(
    add_help=False,
    description="Control the execution of the TuringArena daemon",
)

subparsers = DAEMON_CONTROL_PARSER.add_subparsers(dest="subcommand", metavar="COMMAND")
subparsers.required = True
subparsers.add_parser(
    "start",
    parents=[DaemonStartCommand.PARSER],
    help=DaemonStartCommand.PARSER.description,
).set_defaults(Command=DaemonStartCommand)
subparsers.add_parser(
    "stop",
    parents=[DaemonStopCommand.PARSER],
    help=DaemonStopCommand.PARSER.description,
).set_defaults(Command=DaemonStopCommand)
