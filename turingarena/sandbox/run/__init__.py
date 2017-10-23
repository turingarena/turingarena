import logging
import os
import sys
import tempfile

from . import cpp

OK = 0
EXC = 1

logger = logging.getLogger(__name__)


class SandboxException(Exception):
    pass


class Sandbox:
    def __init__(self, algorithm_name):
        self.algorithm_name = algorithm_name

        prefix = "turingarena_sandbox_{}_".format(self.algorithm_name)

        with tempfile.TemporaryDirectory(prefix=prefix) as sandbox_dir:
            self.sandbox_dir = sandbox_dir
            self.control_request_pipe_name = os.path.join(sandbox_dir, "control_request.pipe")
            self.control_response_pipe_name = os.path.join(sandbox_dir, "control_response.pipe")
            self.downward_pipe_name = os.path.join(sandbox_dir, "downward.pipe")
            self.upward_pipe_name = os.path.join(sandbox_dir, "upward.pipe")

            self.os_process = None
            self.downward_pipe = None
            self.upward_pipe = None

            logger.debug("sandbox folder: %s", sandbox_dir)

            self.prepare()
            self.main_loop()

    def prepare(self):
        logger.debug("creating pipes...")
        os.mkfifo(self.control_request_pipe_name)
        os.mkfifo(self.control_response_pipe_name)
        os.mkfifo(self.downward_pipe_name)
        os.mkfifo(self.upward_pipe_name)
        logger.debug("pipes created")

        print(self.sandbox_dir)
        sys.stdout.close()

    def main_loop(self):
        while True:
            logger.debug("waiting for commands on control request pipe...")
            self.accept_command()

    def accept_command(self):
        with open(self.control_request_pipe_name, "r") as request:
            command = request.readline().strip()
            if command not in self.commands:
                raise ValueError("invalid command", command)
            handler = getattr(self, "command_" + command)(request)

            try:
                next(handler)
                result = OK
            except SandboxException as e:
                result = EXC

        with open(self.control_response_pipe_name, "w") as response:
            print(result, file=response)

        l = list(handler)
        assert not l  # should yield once

    commands = {
        "start",
        "stop",
    }

    def command_start(self, request):
        if self.os_process is not None:
            raise SandboxException("already started")

        yield

        self.downward_pipe = open(self.downward_pipe_name, "r")
        logger.debug("downward pipe opened")
        self.upward_pipe = open(self.upward_pipe_name, "w")
        logger.debug("upward pipe opened")
        logger.debug("starting process...")
        self.os_process = run(
            algorithm_name=self.algorithm_name,
            downward_pipe=self.downward_pipe,
            upward_pipe=self.upward_pipe,
        )
        logger.debug("process started")

    def command_stop(self, request, response):
        if self.os_process is None:
            raise SandboxException("not started")
        yield


sandbox_run = Sandbox
