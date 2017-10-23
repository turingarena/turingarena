import logging
import os

logger = logging.getLogger(__name__)


class SandboxClient:

    def __init__(self):
        self.sandbox_dir = os.environ.get("TURINGARENA_SANDBOX_DIR")

    def is_supported(self):
        return self.sandbox_dir is not None

    def create_process(self, algorithm_name):
        self.check_connected()

        logger.debug("Creating new process for algorithm %s" % algorithm_name)

        response = self.request("create_process", algorithm_name)

        return Process(self, process_id=int(response))

    def request(self, *args):
        with open(self.sandbox_dir + "/control_request.pipe", "w") as p:
            print(*args, file=p)
        with open(self.sandbox_dir + "/control_response.pipe", "r") as p:
            return p.readline().strip()

    def check_connected(self):
        if not self.is_supported():
            raise SystemError(
                "Cannot connect to sandbox manager. Did you run with turingarenasandbox?")


class Process:
    def __init__(self, client, process_id):
        self.client = client
        self.process_id = process_id

        self.downward_pipe = None
        self.upward_pipe = None

    def start(self):
        logger.debug("Starting process with id: %d", self.process_id)
        response = self.client.request("process_start", self.process_id)

        self.downward_pipe = open(
            "%s/process_downward.%d.pipe" % (self.client.sandbox_dir, self.process_id),
            "w", buffering=1)
        self.upward_pipe = open(
            "%s/process_upward.%d.pipe" % (self.client.sandbox_dir, self.process_id),
            "r")
        logger.debug("successfully opened pipes of process %d", self.process_id)
        return int(response)

    def status(self):
        logger.debug("Requesting status of process with id: %d", self.process_id)
        response = self.client.request("process_status", self.process_id)
        return int(response)

    def wait(self):
        logger.debug("Waiting process with id: %d", self.process_id)
        response = self.client.request("process_wait", self.process_id)
        return int(response)

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_val is None:
            self.wait()

sandbox = SandboxClient()
