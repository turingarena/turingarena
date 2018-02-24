from turingarena.cli import docopt_cli
from turingarena.cli.loggerinit import init_logger


@docopt_cli
def main(args):
    """TuringArena protocol driver.

    Usage:
      turingarena-driver <interface> <sandbox>

    Options:
      <interface>  Interface to drive.
      <sandbox>  Sandbox to connect to.
    """

    init_logger()
    # TODO
