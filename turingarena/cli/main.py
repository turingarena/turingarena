"""TuringArena command line interface.

Usage:
  turingarena [options] (container|sandbox|protocol) [<args>]...

Options:
  --log-level=<level>  Set logging level.

Available sub-commands:
  engine  commands that are supposed to run within a container
"""

import docopt

from turingarena.cli.loggerinit import init_logger
from turingarena.container.cli import container_cli
from turingarena.protocol.cli import protocol_cli
from turingarena.sandbox.cli import sandbox_cli


def main():
    args = docopt.docopt(__doc__, options_first=True)
    init_logger(args)

    argv2 = args["<args>"]
    if args["container"]: return container_cli(argv2)
    if args["sandbox"]: return sandbox_cli(argv2)
    if args["protocol"]: return protocol_cli(argv2)
