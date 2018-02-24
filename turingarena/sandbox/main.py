import sys
import tempfile

from turingarena.cli import docopt_cli
from turingarena.cli.loggerinit import init_logger
from turingarena.pipeboundary import PipeBoundarySide
from turingarena.sandbox.connection import SandboxBoundary
from turingarena.sandbox.server import SandboxServer


@docopt_cli
def main(args):
    """TuringArena sandbox server.

    Usage:
      turingarena-sandbox
    """

    init_logger()
    with tempfile.TemporaryDirectory(
            prefix="turingarena_sandbox_provider_",
    ) as directory:
        boundary = SandboxBoundary(directory)
        boundary.init()
        print(directory)
        sys.stdout.close()
        with boundary.connect(PipeBoundarySide.SERVER) as connection:
            server = SandboxServer(connection)
            server.run()
