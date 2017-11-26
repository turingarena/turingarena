import logging
import sys
import threading

import os
import tempfile

from turingarena.sandbox.run.cpp import run_cpp
from . import cpp

OK = 0
EXC = 1

logger = logging.getLogger(__name__)


class SandboxException(Exception):
    pass


class SandboxServer:
    def __init__(self, algorithm_name):
        self.algorithm_name = algorithm_name

        prefix = "turingarena_sandbox_{}_".format(self.algorithm_name)

        with tempfile.TemporaryDirectory(prefix=prefix) as sandbox_dir:
            self.sandbox_dir = sandbox_dir
            self.control_request_pipe_name = os.path.join(sandbox_dir, "control_request.pipe")
            self.control_response_pipe_name = os.path.join(sandbox_dir, "control_response.pipe")
            self.downward_pipe_name = os.path.join(sandbox_dir, "downward.pipe")
            self.upward_pipe_name = os.path.join(sandbox_dir, "upward.pipe")

            self.spawner_thread = None
            self.os_process = None

            logger.debug("sandbox folder: %s", sandbox_dir)

            logger.debug("creating pipes...")
            os.mkfifo(self.control_request_pipe_name)
            os.mkfifo(self.control_response_pipe_name)
            os.mkfifo(self.downward_pipe_name)
            os.mkfifo(self.upward_pipe_name)
            logger.debug("pipes created")

            print(self.sandbox_dir)
            sys.stdout.close()

            self.terminated = False
            self.main_loop()

    def main_loop(self):
        while True:
            logger.debug("waiting for commands on control request pipe...")
            self.accept_command()
            if self.terminated:
                sys.exit()

    def accept_command(self):
        with open(self.control_request_pipe_name, "r") as request:
            command = request.readline().strip()
            if command not in self.commands:
                raise ValueError("invalid command", command)
            logger.debug("received command '{}'".format(command))
            handler = getattr(self, "command_" + command)

            try:
                handler(request)
                logger.debug("handler OK")
                result = OK
            except SandboxException as e:
                logger.exception(e)
                result = EXC

        with open(self.control_response_pipe_name, "w") as response:
            print(result, file=response)

        logger.debug("response sent: {}".format(result))

    commands = {
        "start",
        "kill",
        "wait",
    }

    def command_start(self, request):
        if self.os_process is not None:
            raise SandboxException("already started")

        algorithm_dir = "algorithms/{}/".format(self.algorithm_name)

        with open(algorithm_dir + "language.txt") as language_file:
            language = language_file.read().strip()

        runners = {
            "c++": run_cpp
        }
        runner = runners[language]

        logger.debug("starting process...")

        def spawn():
            logger.debug("opening downward pipe...")
            downward_pipe = open(self.downward_pipe_name, "r")
            logger.debug("opening upward pipe...")
            upward_pipe = open(self.upward_pipe_name, "w")
            logger.debug("pipes opened")

            self.os_process = runner(
                algorithm_dir=algorithm_dir,
                downward_pipe=downward_pipe,
                upward_pipe=upward_pipe,
            )

        # avoid blocking when opening pipes
        self.spawner_thread = threading.Thread(target=spawn)
        self.spawner_thread.start()

        logger.debug("process started")

    def command_kill(self, request):
        if self.spawner_thread is None:
            raise SandboxException("not started")
        logger.debug("joining spawner thread")
        self.spawner_thread.join()
        logger.debug("killing child process")
        self.os_process.kill()

    def command_wait(self, request):
        if self.spawner_thread is None:
            raise SandboxException("not started")
        logger.debug("joining spawner thread")
        self.spawner_thread.join()
        logger.debug("waiting for child process")
        self.os_process.wait()
        logger.debug("wait done")
        self.os_process = None
        self.spawner_thread = None
        self.terminated = True


sandbox_run = SandboxServer
