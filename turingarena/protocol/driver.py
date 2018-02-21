from turingarena.cli import docopt_cli
from turingarena.protocol.server import run_server


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

    run_server(
        protocol_name=args["<protocol>"],
        interface_name=args["<interface>"],
        sandbox_dir=args["<sandbox>"],
    )
