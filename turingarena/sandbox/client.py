import logging
import subprocess
from contextlib import contextmanager

from turingarena.pipeboundary import PipeBoundarySide
from turingarena.sandbox.connection import SandboxProcessBoundary, SandboxProcessWaitBarrier

logger = logging.getLogger(__name__)

class SandboxException(Exception):
    pass


class SandboxClient:
    @contextmanager
    def run(self, algorithm_dir):
        cli = ["turingarena-sandbox", algorithm_dir]
        logger.debug(f"running {cli}")
        with subprocess.Popen(
                cli,
                stdout=subprocess.PIPE,
                universal_newlines=True,
        ) as server_process:
            sandbox_dir = server_process.stdout.readline().strip()
            logger.info("connected to sandbox at {}".format(sandbox_dir))

            try:
                yield SandboxProcessClient(sandbox_dir)
            except Exception as e:
                logger.exception(e)
                raise

            logger.debug("waiting sandbox server process")


class SandboxProcessClient:
    def __init__(self, sandbox_dir):
        self.boundary = SandboxProcessBoundary(sandbox_dir)
        self.wait_barrier = SandboxProcessWaitBarrier(sandbox_dir)

    @contextmanager
    def connect(self):
        logger.debug("connecting to process...")
        with self.boundary.connect(side=PipeBoundarySide.CLIENT) as connection:
            try:
                yield connection
            except Exception as e:
                logger.exception(e)
                raise
            finally:
                logger.debug("reaching wait barrier")
                with self.wait_barrier.connect(side=PipeBoundarySide.CLIENT):
                    pass
