import os
import subprocess
import sys


class AlgorithmProcess:

    def __init__(self, supervisor, process_id, algorithm_name):
        self.supervisor = supervisor
        self.process_id = process_id
        self.algorithm_name = algorithm_name
        self.executable_path = os.path.join(self.supervisor.task_run_dir, "algorithms", algorithm_name, "algorithm")
        self.downward_pipe_name = os.path.join(self.supervisor.driver_sandbox_dir, "algorithm_downward.%d.pipe" % (process_id,))
        self.upward_pipe_name = os.path.join(self.supervisor.driver_sandbox_dir, "algorithm_upward.%d.pipe" % (process_id,))

    def prepare(self):
        os.mkfifo(self.downward_pipe_name)
        os.mkfifo(self.upward_pipe_name)

        print("SUPERVISOR: algorithm process %s(%d): pipes created" % (self.algorithm_name, self.process_id), file=sys.stderr)

    def run(self):
        self.downward_pipe = open(self.downward_pipe_name, "r")
        print("SUPERVISOR: algorithm process %s(%d): downward pipe opened" % (self.algorithm_name, self.process_id), file=sys.stderr)
        self.upward_pipe = open(self.upward_pipe_name, "w")
        print("SUPERVISOR: algorithm process %s(%d): upward pipe opened" % (self.algorithm_name, self.process_id), file=sys.stderr)

        print("SUPERVISOR: algorithm process %s(%d): starting process..." % (self.algorithm_name, self.process_id), file=sys.stderr)
        self.os_process = subprocess.Popen(
            [self.executable_path],
            universal_newlines=True,
            stdin=self.downward_pipe,
            stdout=self.upward_pipe,
            bufsize=1
        )
        print("SUPERVISOR: algorithm process %s(%d): process started" % (self.algorithm_name, self.process_id), file=sys.stderr)

    def status(self):
        # TODO: return something meaningful
        return 0

    def kill(self):
        # TODO: define meaning of return value
        return self.os_process.kill()


class ReadFile:

    def __init__(self, supervisor, file_id, file_name):
        self.supervisor = supervisor
        self.file_id = file_id
        self.file_name = file_name
        self.file_path = os.path.join(self.supervisor.task_run_dir, "read_files", file_name, "data.txt")

    def open(self):
        os.symlink(
            os.path.join("..", self.file_path),
            os.path.join(self.supervisor.driver_sandbox_dir, "read_file.%d.txt" % (self.file_id,)))


class Supervisor:

    def __init__(self, task_run_dir):
        self.algorithm_processes = {}
        self.read_files = {}
        self._next_id = 0

        self.task_run_dir = task_run_dir
        self.driver_sandbox_dir = os.path.join(task_run_dir, "driver_sandbox")
        self.driver_path = os.path.join(self.task_run_dir, "driver", "driver")

        self.control_request_pipe_name = os.path.join(self.driver_sandbox_dir, "control_request.pipe")
        self.control_response_pipe_name = os.path.join(self.driver_sandbox_dir, "control_response.pipe")

    def next_id(self):
        self._next_id += 1
        return self._next_id

    def algorithm_start(self, algorithm_name):
        process_id = self.next_id()
        process = AlgorithmProcess(self, process_id, algorithm_name)
        self.algorithm_processes[process_id] = process

        process.prepare()

        return process_id

    def after_algorithm_start(self, algorithm_name, process_id):
        self.algorithm_processes[process_id].run()

    def algorithm_status(self, process_id):
        process = self.algorithm_processes[process_id]
        return process.status()

    def algorithm_kill(self, process_id):
        process = self.algorithm_processes[process_id]
        return process.kill()

    def read_file_open(self, file_name):
        process_id = self.next_id()
        read_file = ReadFile(self, process_id, file_name)
        self.read_files[process_id] = read_file

        read_file.open()

        return process_id

    def read_file_close(self, file_id):
        pass

    def on_command(self, command, arg):
        commands = {
            "algorithm_start": str,
            "algorithm_status": int,
            "algorithm_kill": int,
            "read_file_open": str,
            "read_file_close": str
        }

        if command not in commands:
            raise ValueError("Unrecognized command: " + command)

        arg_type = commands[command]
        arg_value = arg_type(arg)

        print("SUPERVISOR: received command %s(%s)" % (command, arg_value), file=sys.stderr)
        response = getattr(self, command)(arg_value)
        print("SUPERVISOR: command %s(%s) returned %s" % (command, arg_value, response), file=sys.stderr)

        return response

    def after_command(self, command, arg, result):
        method_name = "after_" + command
        if hasattr(self, method_name):
            getattr(self, method_name)(arg, result)

    def main_loop(self):
        while True:
            print("SUPERVISOR: waiting for commands on control request pipe...", file=sys.stderr)
            line = self.control_request_pipe.readline()
            if not line:
                print("SUPERVISOR: control request pipe closed, terminating.", file=sys.stderr)
                break
            print("SUPERVISOR: received line on control request pipe:", line, file=sys.stderr)

            command, arg = line.rstrip().split(" ", 2)
            result = self.on_command(command, arg)

            print("SUPERVISOR: sending on control response pipe %s" % (result,), file=sys.stderr)
            print(result, file=self.control_response_pipe)
            self.control_response_pipe.flush()
            print("SUPERVISOR: sent on control response pipe %s" % (result,), file=sys.stderr)

            self.after_command(command, arg, result)

    def run(self):
        print("SUPERVISOR: starting in folder:", self.task_run_dir, file=sys.stderr)

        os.mkdir(self.driver_sandbox_dir)

        print("SUPERVISOR: creating control pipes...", file=sys.stderr)
        os.mkfifo(self.control_request_pipe_name)
        os.mkfifo(self.control_response_pipe_name)
        print("SUPERVISOR: control pipes created", file=sys.stderr)
        print("SUPERVISOR: control request pipe: %s" % (self.control_request_pipe_name,), file=sys.stderr)
        print("SUPERVISOR: control response pipe: %s" % (self.control_response_pipe_name,), file=sys.stderr)

        print("SUPERVISOR: starting driver process: %s" % (self.driver_path,), file=sys.stderr)
        print("SUPERVISOR: driver sandbox dir: %s" % (self.driver_sandbox_dir,), file=sys.stderr)

        self.driver = subprocess.Popen(
            [self.driver_path],
            cwd=self.driver_sandbox_dir,
            universal_newlines=True,
            bufsize=1
        )

        print("SUPERVISOR: driver process started", file=sys.stderr)

        print("SUPERVISOR: opening control pipes...", file=sys.stderr)
        self.control_request_pipe = open(self.control_request_pipe_name, "r")
        print("SUPERVISOR: control request pipe opened", file=sys.stderr)
        self.control_response_pipe = open(self.control_response_pipe_name, "w")
        print("SUPERVISOR: control response pipe opened", file=sys.stderr)

        self.main_loop()
