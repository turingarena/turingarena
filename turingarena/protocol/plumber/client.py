import logging

import subprocess

logger = logging.getLogger(__name__)


class PlumberException(Exception):
    pass


class Plumber:
    def __init__(self, interface_name, *, process):
        self.interface_name = interface_name

        self.plumber = subprocess.Popen(
            ["turingarena", "protocol", "plumber", interface_name] + [
                "--downward-pipe", process.downward_pipe_name,
                "--upward-pipe", process.upward_pipe_name,
            ],
            stdout=subprocess.PIPE,
            universal_newlines=True,
        )
        self.plumber_dir = self.plumber.stdout.readline().strip()

        self.downward_pipe = None
        self.upward_pipe = None

        self.plumbing_request_pipe_name = self.plumber_dir + "/plumbing_request.pipe"
        self.plumbing_response_pipe_name = self.plumber_dir + "/plumbing_response.pipe"

    def request(self, *args):
        with open(self.plumbing_request_pipe_name, "w") as p:
            for a in args:
                print(a, file=p)
        with open(self.plumbing_response_pipe_name, "r") as p:
            result = int(p.readline().strip())
            if result:
                raise PlumberException

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.plumber.wait()
