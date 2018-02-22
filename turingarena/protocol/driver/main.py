from turingarena.cli import docopt_cli
from turingarena.protocol.driver.server import DriverServer


@docopt_cli
def main(args):
    """TuringArena protocol driver.

    Usage:
      turingarena-driver <interface> <sandbox>

    Options:
      <interface>  Interface to drive.
      <sandbox>  Sandbox to connect to.
    """

    DriverServer(
        interface=args["<interface>"],
        sandbox_dir=args["<sandbox>"],
    )
