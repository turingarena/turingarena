import logging
import subprocess
import argparse
import os

import sys
from turingarena_cli.common import *

image = "turingarena/turingarena:latest"
name = "turingarena"

# in python 2.x, FileNotFoundError doesn't exists
try:
    FileNotFoundError
except NameError:
    FileNotFoundError = IOError


def check_docker():
    cli = ["docker", "ps"]
    try:
        subprocess.check_output(cli)
    except FileNotFoundError:
        sys.exit("Docker executable not found. Make sure that docker is installed and present in your $PATH")
    except subprocess.CalledProcessError:
        sys.exit("Docker is installed, but the daemon is not running. Try 'systemctl start docker' if you are on Linux")


def update_turingarena():
    logging.info("Upgrading turingarena docker image")
    cli = ["docker", "pull", image]
    subprocess.call(cli)
    logging.info("Remember to also update turingarena CLI with `pip install -U turingarena-cli`")


def check_root():
    if os.getuid() != 0:
        sys.exit("You must be root to execute turingarenad! Try `sudo turingarenad`")


def already_running():
    cli = ["docker", "ps"]
    output = subprocess.check_output(cli)
    return name in str(output)


def kill_daemon():
    logging.info("Killing turingarena daemon")
    cli = ["docker", "kill", name]
    subprocess.check_output(cli)


def parse_cli():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dev-dir", type=str, help="source code directory of TuringArena (for development)")
    parser.add_argument("--upgrade", "-u", help="upgrade turingarena docker image", action="store_true")
    parser.add_argument("--restart", "-r", help="kill daemon if already running", action="store_true")
    parser.add_argument("--kill", "-k", help="kill running turingarena daemon", action="store_true")

    return parser.parse_args()


def run_daemon(dev_dir=None):
    logging.info("Executing Turingarena daemon")
    volumes = []
    if dev_dir:
        dev_dir = os.path.abspath(dev_dir)
        logging.info("Developement mode: mounting {} into the container".format(dev_dir))
        volumes.append("--mount=type=bind,src={},dst=/usr/local/turingarena/,readonly".format(dev_dir))
    cli = [
              "docker",
              "run",
              "--name={}".format(name),
              "--rm",
              "--read-only",
              "--tmpfs=/run/turingarena:exec,mode=1777,uid=1000",
              "--tmpfs=/tmp:exec,mode=1777",
          ] + volumes + [
              "--publish=127.0.0.1:20122:22",
              image,
              "socat",
              "TCP-LISTEN:22,fork",
              """EXEC:"/usr/sbin/sshd -q -i -e -o PermitEmptyPasswords=yes -o Protocol=2",nofork""",
          ]
    logging.info("Running: {}".format(" ".join(cli)))
    subprocess.Popen(cli, cwd="/")
    logging.info("Turingarena is running in background, use `turingarenad --kill` to terminate it")


def main():
    args = parse_cli()

    init_logger(args.log_level)
    check_root()
    check_docker()

    if args.kill:
        return kill_daemon()

    if args.upgrade:
        update_turingarena()
        if not args.restart:
            return

    if already_running():
        if args.restart:
            kill_daemon()
        else:
            sys.exit("Daemon already running, to restart it use --restart option!")

    run_daemon(dev_dir=args.dev_dir)
