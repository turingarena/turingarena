"""TuringArena container CLI.

Usage:
  container [options] <cmd> [<args>...]

Options:
"""

import docopt

from turingarena.container.sshd_cli import container_sshd_cli


def container_cli(argv):
    args = docopt.docopt(__doc__, argv=argv, options_first=True)

    commands = {
        "sshd": container_sshd_cli,
    }
    argv2 = args["<args>"]
    return commands[args["<cmd>"]](argv=argv2)
