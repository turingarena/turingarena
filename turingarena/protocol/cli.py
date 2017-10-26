"""TuringArena interface generator.

Parse and compiles an interface definition file,
and generates interface code for the supported languages.

Usage:
  protocol [options] -p <package> [-f <file>] (skeleton|proxy|plumber) [<args>...]

Options:

  -p --package=<package>  Python package containing the protocol definition
  -f --file=<file>  Name of the protocol definition file inside the package [default: protocol.txt]

"""

import docopt
import pkg_resources

from turingarena.protocol.plumber.cli import protocol_plumber_cli

from turingarena.protocol.proxy.cli import protocol_proxy_cli

from turingarena.protocol.analysis import analyze_protocol
from turingarena.protocol.parser import parse_protocol
from turingarena.protocol.skeleton.cli import protocol_skeleton_cli


def protocol_cli(argv):
    args = docopt.docopt(__doc__, argv=argv, options_first=True)

    package_name = args["--package"]
    protocol_file_name = pkg_resources.resource_filename(package_name, args["--file"])

    protocol = parse_protocol(protocol_file_name)
    protocol.package_name = package_name
    protocol.file_name = protocol_file_name

    analyze_protocol(protocol)

    argv2 = args["<args>"]
    if args["skeleton"]: return protocol_skeleton_cli(protocol=protocol, argv=argv2)
    if args["proxy"]: return protocol_proxy_cli(protocol=protocol, argv=argv2)
    if args["plumber"]: return protocol_plumber_cli(protocol=protocol, argv=argv2)
