"""TuringArena container client.

Usage:
  turingarena-container-client [options] exec <container> [-i <input>]... [-o <output>]... [--] <cmd>...
  turingarena-container-client [options] import <container> <dir>
  turingarena-container-client [options] export <container> <id>

Options:

  --log-level=<level>  Set logging level.
  <cmd>  Command to run

"""

from docopt import docopt

from turingarena.loggerinit import init_logger


def main():
    args = docopt(__doc__)
    init_logger(args)

    if args["exec"]:
        pass # TODO
