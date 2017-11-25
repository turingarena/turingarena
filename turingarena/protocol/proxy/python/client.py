import logging
import subprocess
from contextlib import contextmanager, ExitStack

import os

from turingarena.protocol.proxy.python.engine import ProxyEngine, Proxy
from turingarena.sandbox.client import Algorithm

logger = logging.getLogger(__name__)


class Implementation:
    def __init__(self, *, protocol_id, interface_name, algorithm_name):
        self.protocol_id = protocol_id
        self.interface_name = interface_name
        self.algorithm = Algorithm(algorithm_name)

    @contextmanager
    def run(self, **global_variables):
        interface_signature = self.protocol_id.load_signature(self.interface_name)
        sandbox = self.algorithm.sandbox()
        with sandbox.run() as process:
            plumber = ProxyClient(
                protocol_id=self.protocol_id,
                interface_name=self.interface_name,
                process=process,
            )
            with plumber.connect() as connection:
                engine = ProxyEngine(
                    connection=connection,
                    interface_signature=interface_signature,
                )
                engine.begin_main(**global_variables)
                yield Proxy(engine=engine, interface_signature=interface_signature)
                engine.end_main()


class ProxyClient:
    def __init__(self, *, protocol_id, interface_name, process):
        self.protocol_id = protocol_id
        self.interface_name = interface_name
        self.process = process

    @contextmanager
    def connect(self):
        cli = (
            f"{self.protocol_id.to_command()}"
            f" server"
            f" --interface {self.interface_name}"
            f" --sandbox {self.process.sandbox_dir}"
        )
        with ExitStack() as stack:
            plumber_process = subprocess.Popen(
                cli,
                shell=True,
                stdout=subprocess.PIPE,
                universal_newlines=True,
            )
            stack.enter_context(plumber_process)
            plumber_dir = plumber_process.stdout.readline().strip()

            assert os.path.isdir(plumber_dir)

            logger.debug("opening request pipe...")
            request_pipe = stack.enter_context(open(plumber_dir + "/plumbing_request.pipe", "w"))
            logger.debug("opening response pipe...")
            response_pipe = stack.enter_context(open(plumber_dir + "/plumbing_response.pipe"))
            logger.debug("connected")

            try:
                yield ProxyConnection(
                    request_pipe=request_pipe,
                    response_pipe=response_pipe,
                )
            except Exception as e:
                logger.exception(e)
                raise

            logger.debug("waiting for plumber process")


class ProxyConnection:
    def __init__(self, *, request_pipe, response_pipe):
        self.request_pipe = request_pipe
        self.response_pipe = response_pipe
