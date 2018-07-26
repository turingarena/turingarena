import subprocess
import argparse
import os

from turingarena_cli.common import *


def check_root():
    if os.getuid() != 0:
        error("You must be root to execute turingarenad!")
        exit(1)


def parse_cli():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dev-dir", type=str, help="source code directory of TuringArena (for development)")
    parser.add_argument("--daemon", "-d", help="fork turingarena in background", action="store_true")

    return parser.parse_args()


def main():
    args = parse_cli()
    check_root()

    ok("Executing Turingarena daemon")
    volumes = []
    if args.dev_dir:
        dev_dir = os.path.abspath(args.dev_dir)
        info("Developement mode: mounting {} into the container".format(dev_dir))
        volumes.append("--mount=type=bind,src={},dst=/usr/local/turingarena/,readonly".format(dev_dir))
    cli = [
              "docker",
              "run",
              "--name=turingarena",
              "--rm",
              "--read-only",
              "--tmpfs=/run/turingarena:exec,mode=1777,uid=1000",
              "--tmpfs=/tmp:exec,mode=1777",
          ] + volumes + [
              "--publish=127.0.0.1:20122:22",
              "turingarena/turingarena",
              "socat",
              "TCP-LISTEN:22,fork",
              """EXEC:"/usr/sbin/sshd -q -i -e -o PermitEmptyPasswords=yes -o Protocol=2",nofork""",
          ]
    info("Running: {}".format(" ".join(cli)))
    try:
        if args.daemon:
            process = subprocess.Popen(cli, cwd="/")
            ok("Turingarena is running in background with pid {pid}. Use `kill {pid}` to terminate".format(pid=process.pid))
        else:
            ok("Executing turingarena in foreground. Use CTRL-C to kill it")
            os.execvp("docker", cli)
    except FileNotFoundError:
        error("docker executable doesn't exist. Is docker installed ?")


if __name__ == "__main__":
    main()
