import logging
import os
import subprocess
import threading

import coloredlogs

from turingarena.runner.cpp import run_cpp

logger = logging.getLogger(__name__)
coloredlogs.install(level=logging.DEBUG, logger=logger)


class Process:

    def __init__(self, supervisor, process_id, algorithm_name):
        self.supervisor = supervisor
        self.process_id = process_id

        self.algorithm_name = algorithm_name
        self.os_process = None

        self.downward_pipe_name = os.path.join(self.supervisor.sandbox_dir, "process_downward.%d.pipe" % (process_id,))
        self.downward_pipe = None

        self.upward_pipe_name = os.path.join(self.supervisor.sandbox_dir, "process_upward.%d.pipe" % (process_id,))
        self.upward_pipe = None

    def prepare(self):
        os.mkfifo(self.downward_pipe_name)
        os.mkfifo(self.upward_pipe_name)

        logger.debug("algorithm process %s(%d): pipes created", self.algorithm_name, self.process_id)

    def start(self):
        logger.info("starting process %d (algorithm: %s)", self.process_id, self.algorithm_name)

        return 0

    def run(self):
        self.downward_pipe = open(self.downward_pipe_name, "r")
        logger.debug("algorithm process %s(%d): downward pipe opened" % (self.algorithm_name, self.process_id))
        self.upward_pipe = open(self.upward_pipe_name, "w")
        logger.debug("algorithm process %s(%d): upward pipe opened" % (self.algorithm_name, self.process_id))

        algorithm_dir = "algorithms/{}/".format(self.algorithm_name)

        with open(algorithm_dir + "language.txt") as language_file:
            language = language_file.read().strip()

        runners = {
            "cpp": run_cpp
        }
        runner = runners[language]

        logger.debug("algorithm process %s(%d): starting process..." % (self.algorithm_name, self.process_id))
        self.os_process = runner(
            algorithm_dir=algorithm_dir,
            downward_pipe=self.downward_pipe,
            upward_pipe=self.upward_pipe,
        )
        logger.debug("algorithm process %s(%d): process started" % (self.algorithm_name, self.process_id))

    def wait(self):
        if self.os_process is not None:
            self.os_process.wait()
        # TODO: return something meaningful
        return 0


class SandboxManager:
    def __init__(self, args, sandbox_dir):
        self.processes = {}
        self.read_files = {}
        self._next_id = 0

        self.args = args
        self.sandbox_dir = sandbox_dir

        self.control_request_pipe_name = os.path.join(self.sandbox_dir, "control_request.pipe")
        self.control_request_pipe = None
        self.control_response_pipe_name = os.path.join(self.sandbox_dir, "control_response.pipe")
        self.control_response_pipe = None

    def next_id(self):
        self._next_id += 1
        return self._next_id

    def create_process(self, algorithm_name):
        process_id = self.next_id()

        process = Process(self, process_id, algorithm_name)
        self.processes[process_id] = process

        process.prepare()

        return process_id

    def process_start(self, process_id):
        return self.processes[process_id].start()

    def after_process_start(self, process_id, status):
        self.processes[process_id].run()

    def process_wait(self, process_id):
        process = self.processes[process_id]
        return process.wait()

    def parse_command(self, command, arg_str):
        commands = {
            "create_process": str,
            "process_start": int,
            "process_wait": int,
        }

        if command not in commands:
            raise ValueError("Unrecognized command: " + command)

        arg_type = commands[command]
        arg = arg_type(arg_str)

        return (command, arg)

    def on_command(self, command, arg):
        logger.debug("received command %s(%s)" % (command, arg))
        response = getattr(self, command)(arg)
        logger.debug("command %s(%s) returned %s" % (command, arg, response))

        return response

    def after_command(self, command, arg, result):
        method_name = "after_" + command
        if hasattr(self, method_name):
            getattr(self, method_name)(arg, result)

    def accept_command(self):
        logger.debug("waiting for commands on control request pipe...")

        with open(self.control_request_pipe_name, "r") as p:
            line = p.readline().strip()

        if line == "stop":
            logger.debug("received stop command, terminating.")
            raise StopIteration
        logger.debug("received line on control request pipe %s", line.rstrip())

        command, arg_str = line.split(" ", 2)
        command, arg = self.parse_command(command, arg_str)

        result = self.on_command(command, arg)

        logger.debug("sending on control response pipe %s", result)
        with open(self.control_response_pipe_name, "w") as p:
            print(result, file=p)
        logger.debug("sent on control response pipe %s", result)

        self.after_command(command, arg, result)

    def main_loop(self):
        while True:
            try:
                self.accept_command()
            except StopIteration:
                return

    def run(self):
        logger.debug("sandbox folder: %s", self.sandbox_dir)

        logger.debug("creating control pipes...")
        os.mkfifo(self.control_request_pipe_name)
        os.mkfifo(self.control_response_pipe_name)
        logger.debug("control pipes created")

        logger.debug("control request pipe: %s" % (self.control_request_pipe_name,))
        logger.debug("control response pipe: %s" % (self.control_response_pipe_name,))

        env = os.environ.copy()
        env.update({
            "TURINGARENA_SANDBOX_DIR": self.sandbox_dir,
        })

        with subprocess.Popen(
            self.args,
            env=env,
            universal_newlines=True,
        ) as delegate:

            def main_loop_thread():
                try:
                    self.main_loop()
                except:
                    delegate.terminate()
                    raise

            logger.debug("module process started")
            threading.Thread(target=main_loop_thread).start()

        # kill the other thread by injecting the "stop" command
        with open(self.control_request_pipe_name, "w") as p:
            print("stop", file=p)
