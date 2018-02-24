from turingarena.cli import docopt_cli
from turingarena.cli.loggerinit import init_logger


@docopt_cli
def main(args):
    """TuringArena sandbox server.

    Usage:
      turingarena-sandbox
    """

    init_logger()
    # TODO
