"""TuringArena command line interface.

Usage:
  turingarena [options] <cmd> [<args>]...

Options:
  --log-level=<level>  Set logging level.

Available sub-commands:
  engine  commands that are supposed to run within a container
"""

import docopt

from turingarena.cli.loggerinit import init_logger
from turingarena.evaluation.cli import evaluation_cli
from turingarena.problem.cli import problem_cli
from turingarena.protocol.cli import protocol_cli
from turingarena.sandbox.cli import sandbox_cli


def main():
    args = docopt.docopt(__doc__, options_first=True)
    init_logger(args)

    commands = {
        "sandbox": sandbox_cli,
        "protocol": protocol_cli,
        "evaluation": evaluation_cli,
        "problem": problem_cli,
    }
    argv2 = args["<args>"]
    commands[args["<cmd>"]](argv2)


if __name__ == '__main__':
    main()
