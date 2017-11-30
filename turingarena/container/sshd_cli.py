"""TuringArena container SSH server CLI.

Usage:
  sshd [options]

Options:
  --name=<name>  Name of the container
"""

import docopt

from turingarena.container.sshd import serve_sshd


def container_sshd_cli(argv):
    args = docopt.docopt(__doc__, argv=argv, options_first=True)
    serve_sshd(name=args["--name"])
