"""TuringArena protocol plumber.

Usage:
  plumber [options] <interface> <sandbox-dir>

Options:
  <interface>  Interface to drive.
  <sandbox-dir>  Location of the sandbox.
"""

import docopt

from turingarena.protocol.plumber import run_plumber


def protocol_plumber_cli(*, argv, protocol):
    args = docopt.docopt(__doc__, argv=argv)
    run_plumber(
        protocol=protocol,
        interface_name=args["<interface>"],
        sandbox_dir=args["<sandbox-dir>"],
    )
