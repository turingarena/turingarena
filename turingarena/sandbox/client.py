import logging
from contextlib import contextmanager

from turingarena.pipeboundary import PipeBoundarySide
from turingarena.sandbox.connection import SandboxProcessBoundary, SandboxProcessWaitBarrier, SandboxProcessConnection

logger = logging.getLogger(__name__)


class SandboxException(Exception):
    pass


class SandboxClient:
    def __init__(self, connection):
        self.connection = connection

    @contextmanager
    def run(self, algorithm_dir):
        print(algorithm_dir, file=self.connection.request, flush=True)
        process_dir, = self.connection.response.readline().splitlines()

        logger.info(f"connected to sandbox at {process_dir}")

        try:
            yield SandboxProcessClient(process_dir)
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
        with self.boundary.connect(side=PipeBoundarySide.CLIENT) as pipes:
            try:
                yield SandboxProcessConnection(**pipes)
            except Exception as e:
                logger.exception(e)
                raise
            finally:
                logger.debug("reaching wait barrier")
                with self.wait_barrier.connect(side=PipeBoundarySide.CLIENT):
                    pass
