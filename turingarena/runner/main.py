"""TuringArena sandbox server.

Usage:
  turingarenasandbox <args>...
  turingarenasandbox (-h | --help)

Options:

  <executables-dir>  Directory where algorithm executables are to be found.
  <pipes-dir>  Directory where named pipes are created. Use a temp dir.

"""
import sys
import tempfile

from turingarena.runner.server import SandboxManager


def main():
    with tempfile.TemporaryDirectory(prefix="turingarena_sandbox") as sandbox_dir:
        SandboxManager(sys.argv[1:], sandbox_dir).run()


if __name__ == '__main__':
    main()
