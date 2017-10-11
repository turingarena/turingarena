"""TuringArena sandbox server.

Wraps the execution of a command,
providing a server to run algorithms in a sandbox.

Usage:
  turingarenasandbox [options] [--] <cmd>...

Options:

  --log-level=<level>  Set logging level.
  <cmd>  Command to run

"""
import sys
import tempfile

from docopt import docopt

from turingarena.loggerinit import init_logger
from turingarena.runner.server import SandboxManager


def main():
    args = docopt(__doc__)
    init_logger(args)
    with tempfile.TemporaryDirectory(prefix="turingarena_sandbox_") as sandbox_dir:
        SandboxManager(args["<cmd>"], sandbox_dir).run()


if __name__ == '__main__':
    main()
