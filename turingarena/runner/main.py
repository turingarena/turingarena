"""TuringArena sandbox server.

Wraps the execution of a command,
providing a server to run algorithms in a sandbox.

Usage:
  turingarenasandbox <args>...

"""
import sys
import tempfile

from turingarena.runner.server import SandboxManager


def main():
    with tempfile.TemporaryDirectory(prefix="turingarena_sandbox_") as sandbox_dir:
        SandboxManager(sys.argv[1:], sandbox_dir).run()


if __name__ == '__main__':
    main()
