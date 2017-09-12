import logging
import os
import shutil

import subprocess
import tempfile


class SandboxClient:
    def __init__(self, executables_dir):
        self.pipes_dir = tempfile.mktemp()
        self.executables_dir = executables_dir

        self.logger = logging.getLogger(__name__)

        os.mkdir(self.pipes_dir)
        self.server = subprocess.Popen(
            " ".join([
                "turingarenasandbox",
                self.executables_dir,
                self.pipes_dir,
            ]),
            shell=True,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            universal_newlines=True)

    def __exit__(self, exc_type, exc_val, exc_tb):
        shutil.rmtree(self.pipes_dir)

    def algorithm_create_process(self, algorithm_name):
        self.logger.debug("Creating new process for algorithm %s" % algorithm_name)
        print("algorithm_create_process", algorithm_name, file=self.server.stdin, flush=True)
        process_id = int(self.server.stdout.readline().strip())

        return Process(self, process_id)


class Process:
    def __init__(self, client, process_id):
        self.client = client
        self.server = client.server
        self.process_id = process_id

        self.downward_pipe = None
        self.upward_pipe = None

        self.logger = self.client.logger

    def _read_status(self):
        return int(self.server.stdout.readline().strip())

    def start(self):
        self.logger.debug("Starting process with id: %d", self.process_id)
        print("process_start", self.process_id, file=self.server.stdin, flush=True)
        self.downward_pipe = open(
            "%s/process_downward.%d.pipe" % (self.client.pipes_dir, self.process_id),
            "w", buffering=1)
        self.upward_pipe = open(
            "%s/process_upward.%d.pipe" % (self.client.pipes_dir, self.process_id),
            "r")
        self.logger.debug("successfully opened pipes of process %d", self.process_id)
        return self._read_status()

    def status(self):
        self.logger.debug("Requesting status of process with id: %d", self.process_id)
        print("process_status", self.process_id, file=self.server.stdin, flush=True)
        return self._read_status()

    def stop(self):
        self.logger.debug("Killing process with id: %d", self.process_id)
        print("process_stop", self.process_id, file=self.server.stdin, flush=True)
        return self._read_status()
