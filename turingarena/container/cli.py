import subprocess

from turingarena.cli import docopt_cli
from turingarena.container.sshd import serve_sshd


@docopt_cli
def container_cli(args):
    """TuringArena container CLI.

    Usage:
      container [options] <cmd> [<args>...]

    Options:
      --name=<name>  Name of the container
    """

    commands = {
        "sshd": container_sshd_cli,
        "run": container_run_cli,
        "serve": container_serve_cli,
        "git": container_git_cli,
    }
    argv2 = args["<args>"]
    return commands[args["<cmd>"]](argv=argv2, name=args["--name"])


@docopt_cli
def container_run_cli(args, name):
    """TuringArena container run CLI.

    Usage:
      run [options] <cmd> [<args>...]

    Options:
    """

    subprocess.run(
        [
            "ssh",
            "-o", f"ProxyCommand=socat - UNIX-CONNECT:/var/run/turingarena/{name}/sshd.sock",
            "-o", "UserKnownHostsFile=/dev/null",
            "-o", "StrictHostKeyChecking=no",
            "root@localhost",
            args["<cmd>"],
            *args["<args>"],
        ]
    )


@docopt_cli
def container_sshd_cli(args, name):
    """TuringArena container SSH server CLI.

    Usage:
      sshd [options]

    Options:
    """

    serve_sshd(name)


@docopt_cli
def container_serve_cli(args, name):
    """TuringArena container serve CLI.

    Usage:
      serve [options]

    Options:
      --sudo  Use sudo
      --image=<image>  Docker image to run [default: turingarena]
    """

    sudo = ["sudo"] if args["--sudo"] else []
    subprocess.run(
        [
            *sudo,
            "docker",
            "run",
            "--rm",
            f"--volume=/var/run/turingarena/{name}/:/var/run/turingarena/{name}/",
            args["--image"],
            "container",
            "sshd",
            f"--name={name}",
        ],
    )


@docopt_cli
def container_git_cli(args, name):
    """TuringArena container serve CLI.

    Usage:
      git [--] [<args>...]

    Options:
    """

    ssh_command = (
        f'ssh'
        f' -o ProxyCommand="socat - UNIX-CONNECT:/var/run/turingarena/{name}/sshd.sock"'
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
