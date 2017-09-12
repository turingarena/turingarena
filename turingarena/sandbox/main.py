"""TuringArena sandbox server.

Usage:
  turingarenasandbox <executables-dir> <pipes-dir>
  turingarenasandbox (-h | --help)

Options:

  <executables-dir>  Directory where algorithm executables are to be found.
  <pipes-dir>  Directory where named pipes are created. Use a temp dir.

"""

import docopt

from turingarena.compiler import parser
from turingarena.compiler.analysis.analysis import TaskAnalyzer
from turingarena.compiler.generator import CodeGenerator
from turingarena.sandbox.server import SandboxManagerServer


def main():
    args = docopt.docopt(__doc__)

    SandboxManagerServer(
        pipes_dir=args["<pipes-dir>"],
        executables_dir=args["<executables-dir>"],
    ).run()


if __name__ == '__main__':
    main()
