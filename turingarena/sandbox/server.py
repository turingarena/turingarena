import os
import subprocess
import logging
import threading

import sys


class Process:

    def __init__(self, server, process_id, algorithm_name, executable_path):
        self.logger = logging.getLogger(__name__)

        self.server = server
        self.process_id = process_id

        self.algorithm_name = algorithm_name
        self.executable_path = executable_path
        self.os_process = None

        self.downward_pipe_name = os.path.join(self.server.pipes_dir, "process_downward.%d.pipe" % (process_id,))
        self.downward_pipe = None

        self.upward_pipe_name = os.path.join(self.server.pipes_dir, "process_upward.%d.pipe" % (process_id,))
        self.upward_pipe = None

    def prepare(self):
        os.mkfifo(self.downward_pipe_name)
        os.mkfifo(self.upward_pipe_name)

        self.logger.debug("algorithm process %s(%d): pipes created", self.algorithm_name, self.process_id)

    def start(self):
        self.logger.info("starting process %d (algorithm: %s)", self.process_id, self.algorithm_name)

        return 0

    def run(self):
        self.downward_pipe = open(self.downward_pipe_name, "r")
        self.logger.debug("algorithm process %s(%d): downward pipe opened" % (self.algorithm_name, self.process_id))
        self.upward_pipe = open(self.upward_pipe_name, "w")
        self.logger.debug("algorithm process %s(%d): upward pipe opened" % (self.algorithm_name, self.process_id))

        self.logger.debug("algorithm process %s(%d): starting process..." % (self.algorithm_name, self.process_id))
        self.os_process = subprocess.Popen(
            [self.executable_path],
            universal_newlines=True,
            stdin=self.downward_pipe,
            stdout=self.upward_pipe,
            bufsize=1
        )
        self.logger.debug("algorithm process %s(%d): process started" % (self.algorithm_name, self.process_id))

    def status(self):
        # TODO: return something meaningful
        return 0

    def kill(self):
        self.os_process.kill()
        # TODO: return something meaningful
        return 0


class SandboxManagerServer:

    def __init__(self, pipes_dir, executables_dir):
        self.processes = {}
        self.read_files = {}
        self._next_id = 0

        self.pipes_dir = pipes_dir
        self.executables_dir = executables_dir

        self.logger = logging.getLogger(__name__)

    def next_id(self):
        self._next_id += 1
        return self._next_id

    def algorithm_create_process(self, algorithm_name):
        process_id = self.next_id()
        executable_path = os.path.join(self.executables_dir, algorithm_name)

        process = Process(self, process_id, algorithm_name, executable_path)
        self.processes[process_id] = process

        process.prepare()

        return process_id

    def process_start(self, process_id):
        return self.processes[process_id].start()

    def after_process_start(self, process_id, status):
        self.processes[process_id].run()

    def process_status(self, process_id):
        process = self.processes[process_id]
        return process.status()

    def process_stop(self, process_id):
        process = self.processes[process_id]
        return process.kill()

    def parse_command(self, command, arg_str):
        commands = {
            "algorithm_create_process": str,
            "process_start": int,
            "process_status": int,
            "process_stop": int,
            "read_file_open": str,
            "read_file_close": str
        }

        if command not in commands:
            raise ValueError("Unrecognized command: " + command)

        arg_type = commands[command]
        arg = arg_type(arg_str)

        return (command, arg)

    def on_command(self, command, arg):
        self.logger.debug("received command %s(%s)" % (command, arg))
        response = getattr(self, command)(arg)
        self.logger.debug("command %s(%s) returned %s" % (command, arg, response))

        return response

    def after_command(self, command, arg, result):
        method_name = "after_" + command
        if hasattr(self, method_name):
            getattr(self, method_name)(arg, result)

    def accept_command(self):
        self.logger.debug("waiting for commands on stdin...")
        line = sys.stdin.readline()
        if not line:
            self.logger.debug("stdin closed, terminating.")
            raise StopIteration
        self.logger.debug("received line on stdin %s", line.rstrip())

        command, arg_str = line.rstrip().split(" ", 2)
        command, arg = self.parse_command(command, arg_str)

        result = self.on_command(command, arg)

        self.logger.debug("sending control response %s", result)
        print(result)
        sys.stdout.flush()
        self.logger.debug("sent control response %s", result)

        self.after_command(command, arg, result)

    def run(self):
        self.logger.debug("sandbox folder: %s", self.pipes_dir)
        while True:
            try:
                self.accept_command()
            except StopIteration:
                return
