import logging
from contextlib import contextmanager

from turingarena.pipeboundary import PipeBoundarySide, PipeBoundary
from turingarena.sandbox.connection import SandboxProcessConnection, \
    SANDBOX_PROCESS_CHANNEL, SANDBOX_WAIT_BARRIER, SANDBOX_QUEUE

logger = logging.getLogger(__name__)


class SandboxException(Exception):
    pass


class SandboxClient:
    def __init__(self, sandbox_dir):
        self.boundary = PipeBoundary(sandbox_dir)

    @contextmanager
    def run(self, algorithm_dir):
        response = self.boundary.send_request(
            SANDBOX_QUEUE,
            algorithm_dir=algorithm_dir,
        )

        process_dir = response["sandbox_process_dir"]

        logger.info(f"connected to sandbox at {process_dir}")

        try:
            yield SandboxProcessClient(process_dir)
        except Exception as e:
            logger.exception(e)
            raise


class SandboxProcessClient:
    def __init__(self, sandbox_dir):
        self.boundary = PipeBoundary(sandbox_dir)

    @contextmanager
    def connect(self):
        logger.debug("connecting to process...")
        with self.boundary.open_channel(SANDBOX_PROCESS_CHANNEL, PipeBoundarySide.CLIENT) as pipes:
            try:
                yield SandboxProcessConnection(**pipes)
            except Exception as e:
                logger.exception(e)
                raise
            finally:
                logger.debug("reaching wait barrier")
                with self.boundary.open_channel(SANDBOX_WAIT_BARRIER, PipeBoundarySide.CLIENT):
                    pass
