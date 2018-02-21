from turingarena.cli import docopt_cli

from turingarena.cli.loggerinit import init_logger
from turingarena.container.cli import container_cli
from turingarena.make.cli import make_cli
from turingarena.protocol.cli import protocol_cli
from turingarena.sandbox.main import main


@docopt_cli
def main(args):
    """TuringArena command line interface.

    Usage:
      turingarena [options] <cmd> [<args>]...

    Options:
      --log-level=<level>  Set logging level.
    """
    init_logger(args)

    commands = {
        "container": container_cli,
        "sandbox": main,
        "protocol": protocol_cli,
        "make": make_cli,
    }
    argv2 = args["<args>"]
    commands[args["<cmd>"]](argv2)


if __name__ == '__main__':
    main()
