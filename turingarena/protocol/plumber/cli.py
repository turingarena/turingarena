"""TuringArena protocol plumber.

Usage:
  plumber [options] <interface>

Options:
  <interface>  Interface to drive.
  -d --downward-pipe=<file>  Downward pipe.
  -u --upward-pipe=<file>  Upward pipe.
"""

import docopt

from turingarena.protocol.plumber import run_plumber


def protocol_plumber_cli(*, argv, protocol):
    args = docopt.docopt(__doc__, argv=argv)
    interface_name = args["<interface>"]
    run_plumber(
        protocol=protocol,
        interface=protocol.interfaces[interface_name],
        upward_pipe_name=args["--upward-pipe"],
        downward_pipe_name=args["--downward-pipe"],
    )
