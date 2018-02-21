from turingarena.cli import docopt_cli
from turingarena.protocol.driver.server import DriverServer


@docopt_cli
def main(args):
    """TuringArena protocol driver.

    Usage:
      turingarena-driver <protocol> <interface> <sandbox>

    Options:
      <protocol>  Protocol defining the desired interface.
      <interface>  Interface to drive.
      <sandbox>  Sandbox to connect to.
    """

    DriverServer(
        protocol_name=args["<protocol>"],
        interface_name=args["<interface>"],
        sandbox_dir=args["<sandbox>"],
    )
