import logging
import os
import tempfile

import sys
from contextlib import ExitStack

logger = logging.getLogger(__name__)


class PlumberServer:
    def __init__(self, *, protocol, interface, downward_pipe_name, upward_pipe_name):
        prefix = "turingarena_plumber"

        with ExitStack() as stack:
            self.plumber_dir = stack.enter_context(tempfile.TemporaryDirectory(prefix=prefix))
            self.request_pipe_name = os.path.join(self.plumber_dir, "plumbing_request.pipe")
            self.response_pipe_name = os.path.join(self.plumber_dir, "plumbing_response.pipe")

            logger.debug("opening downward/upward pipes")
            self.downward_pipe = stack.enter_context(open(downward_pipe_name, "w"))
            logger.debug("downward pipe opened")
            self.upward_pipe = stack.enter_context(open(upward_pipe_name, "r"))
            logger.debug("upward pipe opened")

            self.prepare()
            self.main_loop()


    def prepare(self):
        logger.debug("creating pipes...")
        os.mkfifo(self.request_pipe_name)
        os.mkfifo(self.response_pipe_name)
        logger.debug("pipes created")

        print(self.plumber_dir)
        sys.stdout.close()

    def main_loop(self):
        pass


run_plumber = PlumberServer
