"""TuringArena protocol.

Usage:
  protocol [options] -n <name> <cmd> [<args>...]

Options:
  -n --name=<name>  Name of the protocol (formatted like a python module)

"""

import docopt

from turingarena.protocol.server.cli import protocol_server_cli


def protocol_cli(argv):
    args = docopt.docopt(__doc__, argv=argv, options_first=True)

    protocol_name = args["--name"]

    commands = {
        "server": protocol_server_cli,
    }
    argv2 = args["<args>"]
    return commands[args["<cmd>"]](protocol_name=protocol_name, argv=argv2)
