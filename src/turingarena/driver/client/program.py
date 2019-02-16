import logging
import os
import subprocess
import threading
from collections import namedtuple
from contextlib import ExitStack, contextmanager

from turingarena.driver.client.connection import DriverProcessConnection
from turingarena.driver.client.exceptions import InterfaceExit
from turingarena.driver.client.process import Process


class Program(namedtuple("Program", [
    "source_path", "interface_path",
])):
    def _open_pipes(self, stack: ExitStack):
        return [
            stack.enter_context(open(fd, mode))
            for fd, mode in zip(os.pipe(), ("r", "w"))
        ]

    @contextmanager
    def _run_server_in_thread(self, downward_tee, upward_tee):
        with ExitStack() as stack:
            client_upward, server_upward = self._open_pipes(stack)
            server_downward, client_downward = self._open_pipes(stack)

            def server_thread():
                try:
                    from turingarena.driver.server import run_server
                    run_server(DriverProcessConnection(
                        upward=server_upward,
                        downward=server_downward,
                    ), self.source_path, self.interface_path, downward_tee=downward_tee, upward_tee=upward_tee)

                    logging.debug("driver server terminated")
                except Exception as e:
                    logging.exception(f"server terminated with exception")
                finally:
                    server_upward.close()
                    server_downward.close()

            thread = threading.Thread(target=server_thread)
            thread.start()

            yield DriverProcessConnection(
                upward=client_upward,
                downward=client_downward,
            )

            stack.callback(thread.join)

    @contextmanager
    def _run_server_in_process(self, downward_tee, upward_tee):
        with subprocess.Popen(
                [
                    "python3",
                    "-m",
                    "turingarena.driver.server",
                    self.source_path,
                    self.interface_path,
                    downward_tee,
                    upward_tee,
                ],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                universal_newlines=True,
        ) as p:
            yield DriverProcessConnection(
                downward=p.stdin,
                upward=p.stdout,
            )

    @contextmanager
    def run(self, downward_tee="/dev/null", upward_tee="/dev/null", **kwargs):
        with ExitStack() as stack:
            driver_connection = stack.enter_context(self._run_server_in_thread(downward_tee, upward_tee))

            process = Process(driver_connection)
            with process._run(**kwargs):
                yield process
