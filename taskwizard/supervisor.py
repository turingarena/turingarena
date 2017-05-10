import os
import shutil
import subprocess
import sys


def trace(*args):
    print("SUPERVISOR:", *args, file=sys.stderr)


class Process:

    def __init__(self, supervisor, process_id, algorithm_name):
        self.supervisor = supervisor
        self.process_id = process_id
        self.algorithm_name = algorithm_name
        self.executable_path = os.path.join(self.supervisor.task_run_dir, "algorithms", algorithm_name, "algorithm")
        self.downward_pipe_name = os.path.join(self.supervisor.module_sandbox_dir, "process_downward.%d.pipe" % (process_id,))
        self.upward_pipe_name = os.path.join(self.supervisor.module_sandbox_dir, "process_upward.%d.pipe" % (process_id,))

    def prepare(self):
        os.mkfifo(self.downward_pipe_name)
        os.mkfifo(self.upward_pipe_name)

        trace("algorithm process %s(%d): pipes created" % (self.algorithm_name, self.process_id))

    def start(self):
        return 0

    def run(self):
        self.downward_pipe = open(self.downward_pipe_name, "r")
        trace("algorithm process %s(%d): downward pipe opened" % (self.algorithm_name, self.process_id))
        self.upward_pipe = open(self.upward_pipe_name, "w")
        trace("algorithm process %s(%d): upward pipe opened" % (self.algorithm_name, self.process_id))

        trace("algorithm process %s(%d): starting process..." % (self.algorithm_name, self.process_id))
        self.os_process = subprocess.Popen(
            [self.executable_path],
            universal_newlines=True,
            stdin=self.downward_pipe,
            stdout=self.upward_pipe,
            bufsize=1
        )
        trace("algorithm process %s(%d): process started" % (self.algorithm_name, self.process_id))

    def status(self):
        # TODO: return something meaningful
        return 0

    def kill(self):
        self.os_process.kill()
        # TODO: return something meaningful
        return 0


class ReadFile:

    def __init__(self, supervisor, file_id, file_name):
        self.supervisor = supervisor
        self.file_id = file_id
        self.file_name = file_name
        self.file_path = os.path.join(self.supervisor.task_run_dir, "read_files", file_name, "data.txt")

    def open(self):
        os.symlink(
            os.path.join("..", self.file_path),
            os.path.join(self.supervisor.module_sandbox_dir, "read_file.%d.txt" % (self.file_id,)))


class Supervisor:

    def __init__(self, task_run_dir):
        self.processes = {}
        self.read_files = {}
        self._next_id = 0

        self.task_run_dir = task_run_dir
        self.module_sandbox_dir = os.path.join(task_run_dir, "module_sandbox")
        self.module_path = os.path.join(task_run_dir, "module", "module")

        self.control_request_pipe_name = os.path.join(self.module_sandbox_dir, "control_request.pipe")
        self.control_response_pipe_name = os.path.join(self.module_sandbox_dir, "control_response.pipe")

        self.parameter_path = os.path.join(task_run_dir, "parameter.txt")
        self.seed_path = os.path.join(task_run_dir, "seed.txt")
        self.result_path = os.path.join(task_run_dir, "result.txt")

    def next_id(self):
        self._next_id += 1
        return self._next_id

    def algorithm_create_process(self, algorithm_name):
        process_id = self.next_id()
        process = Process(self, process_id, algorithm_name)
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

    def read_file_open(self, file_name):
        process_id = self.next_id()
        read_file = ReadFile(self, process_id, file_name)
        self.read_files[process_id] = read_file

        read_file.open()

        return process_id

    def read_file_close(self, file_id):
        pass

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
        trace("received command %s(%s)" % (command, arg))
        response = getattr(self, command)(arg)
        trace("command %s(%s) returned %s" % (command, arg, response))

        return response

    def after_command(self, command, arg, result):
        method_name = "after_" + command
        if hasattr(self, method_name):
            getattr(self, method_name)(arg, result)

    def main_loop(self):
        while True:
            trace("waiting for commands on control request pipe...")
            line = self.control_request_pipe.readline()
            if not line:
                trace("control request pipe closed, terminating.")
                break
            trace("received line on control request pipe:", line.rstrip())

            command, arg_str = line.rstrip().split(" ", 2)
            command, arg = self.parse_command(command, arg_str)

            result = self.on_command(command, arg)

            trace("sending on control response pipe %s" % (result,))
            print(result, file=self.control_response_pipe)
            self.control_response_pipe.flush()
            trace("sent on control response pipe %s" % (result,))

            self.after_command(command, arg, result)

    def run(self):
        trace("starting in folder:", self.task_run_dir)

        os.mkdir(self.module_sandbox_dir)

        trace("creating control pipes...")
        os.mkfifo(self.control_request_pipe_name)
        os.mkfifo(self.control_response_pipe_name)
        trace("control pipes created")
        trace("control request pipe: %s" % (self.control_request_pipe_name,))
        trace("control response pipe: %s" % (self.control_response_pipe_name,))

        trace("starting module process: %s" % (self.module_path,))
        trace("module sandbox dir: %s" % (self.module_sandbox_dir,))

        shutil.copyfile(
            os.path.join(self.task_run_dir, "parameter.txt"),
            os.path.join(self.module_sandbox_dir, "parameter.txt"))

        shutil.copyfile(
            os.path.join(self.task_run_dir, "seed.txt"),
            os.path.join(self.module_sandbox_dir, "seed.txt"))

        self.module = subprocess.Popen(
            [self.module_path],
            cwd=self.module_sandbox_dir,
            universal_newlines=True,
            stdin=open(self.parameter_path),
            stdout=open(self.result_path, "w"),
            bufsize=1
        )

        trace("module process started")

        trace("opening control pipes...")
        self.control_request_pipe = open(self.control_request_pipe_name, "r")
        trace("control request pipe opened")
        self.control_response_pipe = open(self.control_response_pipe_name, "w")
        trace("control response pipe opened")

        self.main_loop()
