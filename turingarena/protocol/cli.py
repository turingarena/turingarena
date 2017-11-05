"""TuringArena protocol.

Usage:
  protocol [options] -n <name> <cmd> [<args>...]

Options:
  -n --name=<name>  Name of the protocol (formatted like a python module)

"""

import docopt

from turingarena.protocol import ProtocolIdentifier
from turingarena.protocol.install.cli import protocol_install_cli
from turingarena.protocol.proxy.cli import protocol_proxy_cli
from turingarena.protocol.server.cli import protocol_server_cli
from turingarena.protocol.skeleton.cli import protocol_skeleton_cli


def protocol_cli(argv):
    args = docopt.docopt(__doc__, argv=argv, options_first=True)

    protocol_id = ProtocolIdentifier(name=args["--name"])

    commands = {
        "install": protocol_install_cli,
        "skeleton": protocol_skeleton_cli,
        "proxy": protocol_proxy_cli,
        "server": protocol_server_cli,
    }
    argv2 = args["<args>"]
    return commands[args["<cmd>"]](protocol_id=protocol_id, argv=argv2)
