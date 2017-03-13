import os
import subprocess
import sys


class Process:

    def __init__(self, supervisor, process_id, algorithm_name):
        self.supervisor = supervisor
        self.process_id = process_id
        self.algorithm_name = algorithm_name
        self.executable_path = os.path.join(self.supervisor.task_run_dir, "algorithms", algorithm_name, "algorithm")
        self.downward_pipe_name = os.path.join(self.supervisor.driver_sandbox_dir, "process_downward.%d.pipe" % (process_id,))
        self.upward_pipe_name = os.path.join(self.supervisor.driver_sandbox_dir, "process_upward.%d.pipe" % (process_id,))

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
            os.path.join(self.supervisor.driver_sandbox_dir, "read_file.%d.txt" % (self.file_id,)))


class Supervisor:

    def __init__(self, task_run_dir):
        self.processes = {}
        self.read_files = {}
        self._next_id = 0

        self.task_run_dir = task_run_dir
        self.driver_sandbox_dir = os.path.join(task_run_dir, "driver_sandbox")
        self.driver_path = os.path.join(task_run_dir, "driver", "driver")

        self.parameter_path = os.path.join(task_run_dir, "parameter.txt")
        self.summary_path = os.path.join(task_run_dir, "summary.txt")

    def next_id(self):
        self._next_id += 1
        return self._next_id

    def algorithm_start(self, algorithm_name):
        process_id = self.next_id()
        process = Process(self, process_id, algorithm_name)
        self.processes[process_id] = process

        process.prepare()

        return process_id

    def after_algorithm_start(self, algorithm_name, process_id):
        self.processes[process_id].run()

    def process_status(self, process_id):
        process = self.processes[process_id]
        return process.status()

    def process_kill(self, process_id):
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

    def on_command(self, command, arg):
        commands = {
            "algorithm_start": str,
            "process_status": int,
            "process_kill": int,
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
            print("SUPERVISOR: received line on control request pipe:", line.rstrip(), file=sys.stderr)

            command, arg = line.rstrip().split(" ", 2)
            result = self.on_command(command, arg)

            print("SUPERVISOR: sending on control response pipe %s" % (result,), file=sys.stderr)
            print(result, file=self.control_response_pipe)
            self.control_response_pipe.flush()
            print("SUPERVISOR: sent on control response pipe %s" % (result,), file=sys.stderr)

            self.after_command(command, arg, result)

    def run(self):
        print("SUPERVISOR: starting in folder:", self.task_run_dir, file=sys.stderr)

        print("SUPERVISOR: driver sandbox dir: %s" % (self.driver_sandbox_dir,), file=sys.stderr)
        os.mkdir(self.driver_sandbox_dir)


        print("SUPERVISOR: creating control pipes...", file=sys.stderr)
        control_request_pipe_fd, control_request_pipe_driver_fd = os.pipe()
        control_response_pipe_driver_fd, control_response_pipe_fd = os.pipe()


        print("SUPERVISOR: starting driver process: %s" % (self.driver_path,), file=sys.stderr)
        self.driver = subprocess.Popen(
            [self.driver_path],
            cwd=self.driver_sandbox_dir,
            universal_newlines=True,
            bufsize=1,
            stdin=os.fdopen(control_response_pipe_driver_fd),
            stdout=os.fdopen(control_request_pipe_driver_fd)
        )

        print("SUPERVISOR: driver process started", file=sys.stderr)

        print("SUPERVISOR: setting control pipes...", file=sys.stderr)
        self.control_request_pipe = os.fdopen(control_request_pipe_fd, "r")
        self.control_response_pipe = os.fdopen(control_response_pipe_fd, "w")
        print("SUPERVISOR: control pipes set", file=sys.stderr)
        self.main_loop()
