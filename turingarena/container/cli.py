"""TuringArena container manager.

Usage:
  container [options] client [<args>]...

Options:
  -h --help  Show this help.
"""
import docopt

from turingarena.container.client import container_client_cli


def container_cli(argv):
    args = docopt.docopt(__doc__, argv=argv, options_first=True)

    if args["client"]: return container_client_cli(args["<args>"])
