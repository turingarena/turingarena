"""TuringArena protocol plumber.

Usage:
  plumber [options] <interface> <sandbox-dir>

Options:
  <interface>  Interface to drive.
  <sandbox-dir>  Location of the sandbox.
"""

import docopt

from turingarena.protocol.server import run_server


def protocol_server_cli(*, argv, protocol):
    args = docopt.docopt(__doc__, argv=argv)
    run_server(
        protocol=protocol,
        interface_name=args["<interface>"],
        sandbox_dir=args["<sandbox-dir>"],
    )
