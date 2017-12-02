from turingarena.cli import docopt_cli
from turingarena.container.sshd import serve_sshd


@docopt_cli
def container_cli(args):
    """TuringArena container CLI.

    Usage:
      container [options] <cmd> [<args>...]

    Options:
    """

    commands = {
        "sshd": container_sshd_cli,
    }
    argv2 = args["<args>"]
    return commands[args["<cmd>"]](argv=argv2)


@docopt_cli
def container_sshd_cli(args):
    """TuringArena container SSH server CLI.

    Usage:
      sshd [options]

    Options:
      --name=<name>  Name of the container
    """

    serve_sshd(name=args["--name"])
