import os
import subprocess
import sys


def logged(fun):
    def logged_fun(self, *args):
        print("SUPERVISOR: Called function", fun.__name__, *args, file=sys.stderr)
        ret = fun(self, *args)
        print("SUPERVISOR: Function", fun.__name__, *args, "returned", ret, file=sys.stderr)
        return ret
    return logged_fun


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

        print("SUPERVISOR: Pipes created", file=sys.stderr)

    def run(self):
        self.downward_pipe = open(self.downward_pipe_name, "r")
        print("SUPERVISOR: Downward pipe opened", file=sys.stderr)
        self.upward_pipe = open(self.upward_pipe_name, "w")
        print("SUPERVISOR: Upward pipe opened", file=sys.stderr)

        print("SUPERVISOR: Pipes opened", file=sys.stderr)

        self.process = subprocess.Popen(
            [self.executable_path],
            universal_newlines=True,
            stdin=self.downward_pipe,
            stdout=self.upward_pipe,
            bufsize=1
        )

        print("SUPERVISOR: Algorithm process started", file=sys.stderr)


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

    def next_id(self):
        self._next_id += 1
        return self._next_id

    @logged
    def algorithm_start(self, algorithm_name):
        process_id = self.next_id()
        process = AlgorithmProcess(self, process_id, algorithm_name)
        self.algorithm_processes[process_id] = process

        process.prepare()

        return process_id

    def after_algorithm_start(self, algorithm_name, process_id):
        self.algorithm_processes[process_id].run()

    @logged
    def algorithm_status(self, process_id):
        pass

    @logged
    def algorithm_kill(self, process_id):
        pass

    @logged
    def read_file_open(self, file_name):
        process_id = self.next_id()
        read_file = ReadFile(self, process_id, file_name)
        self.read_files[process_id] = read_file

        read_file.open()

        return process_id

    @logged
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
        return getattr(self, command)(arg_type(arg))

    def after_command(self, command, arg, result):
        method_name = "after_" + command
        if hasattr(self, method_name):
            getattr(self, method_name)(arg, result)

    def main_loop(self):
        while True:
            line = self.driver.stdout.readline()
            if not line:
                print("SUPERVISOR: control pipe closed, terminating.")
                break
            print("SUPERVISOR: received line:", line)

            command, arg = line.rstrip().split(" ", 2)
            result = self.on_command(command, arg)
            print(result, file=self.driver.stdin)

            self.after_command(command, arg, result)

    def run(self):
        print("Starting supervisor in folder: ", self.task_run_dir, file=sys.stderr)

        os.mkdir(self.driver_sandbox_dir)

        self.driver = subprocess.Popen(
            [self.driver_path],
            cwd=self.driver_sandbox_dir,
            universal_newlines=True,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            bufsize=1  # line buffered
        )

        self.main_loop()
