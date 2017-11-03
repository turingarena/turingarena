"""TuringArena interface generator.

Parse and compiles an interface definition file,
and generates interface code for the supported languages.

Usage:
  protocol [options] -p <package> [-f <file>] <cmd> [<args>...]

Options:

  -p --package=<package>  Python package containing the protocol definition
  -f --file=<file>  Name of the protocol definition file inside the package [default: protocol.txt]

"""

import docopt
import pkg_resources

from turingarena.protocol.model.model import Protocol
from turingarena.protocol.parser import parse_protocol
from turingarena.protocol.proxy.cli import protocol_proxy_cli
from turingarena.protocol.server.cli import protocol_server_cli
from turingarena.protocol.skeleton.cli import protocol_skeleton_cli


def protocol_cli(argv):
    args = docopt.docopt(__doc__, argv=argv, options_first=True)

    package_name = args["--package"]
    protocol_file_name = pkg_resources.resource_filename(package_name, args["--file"])

    protocol = Protocol.compile(
        ast=parse_protocol(protocol_file_name),
        package_name=package_name,
        file_name=protocol_file_name,
    )

    commands = {
        "skeleton": protocol_skeleton_cli,
        "proxy": protocol_proxy_cli,
        "server": protocol_server_cli,
    }
    argv2 = args["<args>"]
    return commands[args["<cmd>"]](protocol=protocol, argv=argv2)
