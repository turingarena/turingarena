import subprocess
import argparse
import os

from turingarena_cli.common import *


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dev-dir", type=str, help="source code directory of TuringArena (for development)")
    parser.add_argument("--daemon", "-d", help="fork turingarena in background", action="store_true")

    args = parser.parse_args()

    volumes = []
    if args.dev_dir is not None:
        dev_dir = os.path.abspath(args.dev_dir)
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
    ok("Executing Turingarena daemon")
    info(str(cli))

    if args.daemon:
        process = subprocess.Popen(cli, cwd="/")
        ok("Turingarena is running in background with pid {}".format(process.pid))
    else:
        ok("Executing turingarena in foreground")
        os.execvp("docker", cli)


if __name__ == "__main__":
    main()
