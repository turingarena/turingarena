"""TuringArena interface generator.

Parse and compiles an interface definition file,
and generates interface code for the supported languages.

Usage:
  protocol [options] -p <package> [-f <file>] (skeleton|proxy|server) [<args>...]

Options:

  -p --package=<package>  Python package containing the protocol definition
  -f --file=<file>  Name of the protocol definition file inside the package [default: protocol.txt]

"""

import docopt
import pkg_resources

from turingarena.protocol.model.statements import Protocol
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

    argv2 = args["<args>"]
    if args["skeleton"]: return protocol_skeleton_cli(protocol=protocol, argv=argv2)
    if args["proxy"]: return protocol_proxy_cli(protocol=protocol, argv=argv2)
    if args["server"]: return protocol_server_cli(protocol=protocol, argv=argv2)
