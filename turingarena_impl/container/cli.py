import logging
import subprocess

from turingarena_impl.cli import docopt_cli

logger = logging.getLogger(__name__)

SOCKET_PATH = "/run/turingarena/sshd.sock"


@docopt_cli
def container_cli(args):
    """TuringArena container CLI.

    Usage:
      container [options] <cmd> [<args>...]
    """

    commands = {
        "git": container_git_cli,
    }
    argv2 = args["<args>"]
    return commands[args["<cmd>"]](argv=argv2)



@docopt_cli
def container_git_cli(args):
    """TuringArena container git CLI.

    Usage:
      git [--] [<args>...]

    Options:
    """

    ssh_command = (
        f'ssh'
        f' -o ProxyCommand="socat - UNIX-CONNECT:{SOCKET_PATH}"'
        f' -o UserKnownHostsFile=/dev/null'
        f' -o StrictHostKeyChecking=no'
    )

    subprocess.run(
        [
            "git",
            *args["<args>"],
        ],
        env={
            "GIT_SSH_COMMAND": ssh_command
        },
    )
