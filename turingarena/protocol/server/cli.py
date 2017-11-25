"""TuringArena protocol plumber.

Usage:
  server [options]

Options:
  -I --interface=<interface>  Interface to drive.
  -s --sandbox=<sandbox>  Sandbox to connect to.
"""

import docopt

from turingarena.protocol.server import run_server


def protocol_server_cli(*, argv, protocol_name):
    args = docopt.docopt(__doc__, argv=argv)
    run_server(
        protocol_name=protocol_name,
        interface_name=args["--interface"],
        sandbox_dir=args["--sandbox"],
    )
