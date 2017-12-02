from turingarena.cli import docopt_cli
from turingarena.protocol.server import run_server


@docopt_cli
def protocol_cli(args):
    """TuringArena protocol.

    Usage:
      protocol [options] -n <name> <cmd> [<args>...]

    Options:
      -n --name=<name>  Name of the protocol (formatted like a python module)

    """

    protocol_name = args["--name"]

    commands = {
        "server": protocol_server_cli,
    }
    argv2 = args["<args>"]
    return commands[args["<cmd>"]](protocol_name=protocol_name, argv=argv2)


@docopt_cli
def protocol_server_cli(args, *, protocol_name):
    """TuringArena protocol server.

    Usage:
      server [options]

    Options:
      -I --interface=<interface>  Interface to drive.
      -s --sandbox=<sandbox>  Sandbox to connect to.
    """

    run_server(
        protocol_name=protocol_name,
        interface_name=args["--interface"],
        sandbox_dir=args["--sandbox"],
    )
