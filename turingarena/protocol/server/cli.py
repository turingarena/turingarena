"""TuringArena protocol plumber.

Usage:
  server [options]

Options:
  -I --interface=<interface>  Interface to drive.
  -s --sandbox=<sandbox>  Sandbox to connect to.
"""

import docopt

from turingarena.protocol.server import run_server


def protocol_server_cli(*, argv, protocol_id):
    args = docopt.docopt(__doc__, argv=argv)
    run_server(
        protocol_id=protocol_id,
        interface_name=args["--interface"],
        sandbox_dir=args["--sandbox"],
    )
