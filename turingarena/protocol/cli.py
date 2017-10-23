"""TuringArena interface generator.

Parse and compiles an interface definition file,
and generates interface code for the supported languages.

Usage:
  protocol [options] (skeleton|proxy|plumber) [<args>...]

Options:

  -i --input=<file>  File containing the interface definition [default: protocol.txt].
  -o --output-dir=<output-dir>  Directory where to generate code [default: ./generated]

"""

import docopt
from turingarena.protocol.plumber.cli import protocol_plumber_cli

from turingarena.protocol.proxy.cli import protocol_proxy_cli

from turingarena.protocol.analysis import analyze_protocol
from turingarena.protocol.parser import parse_protocol
from turingarena.protocol.skeleton.cli import protocol_skeleton_cli


def protocol_cli(argv):
    args = docopt.docopt(__doc__, argv=argv, options_first=True)

    protocol = parse_protocol(args["--input"])
    analyze_protocol(protocol)

    dest_dir = args["--output-dir"]
    # FIXME: not needed by all subcommands

    argv2 = args["<args>"]
    if args["skeleton"]: return protocol_skeleton_cli(protocol=protocol, dest_dir=dest_dir, argv=argv2)
    if args["proxy"]: return protocol_proxy_cli(protocol=protocol, dest_dir=dest_dir, argv=argv2)
    if args["plumber"]: return protocol_plumber_cli(protocol=protocol, argv=argv2)
