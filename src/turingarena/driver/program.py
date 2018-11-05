import logging
import os
import subprocess
import threading
from collections import namedtuple
from contextlib import ExitStack, contextmanager

from turingarena.driver.exceptions import InterfaceExit
from turingarena.driver.connection import DriverProcessConnection
from turingarena.driver.process import Process


class Program(namedtuple("Program", [
    "source_path", "interface_path",
])):
    def _open_pipes(self, stack: ExitStack):
        return [
            stack.enter_context(open(fd, mode))
            for fd, mode in zip(os.pipe(), ("r", "w"))
        ]

    @contextmanager
    def _run_server_in_thread(self):
        with ExitStack() as stack:
            client_upward, server_upward = self._open_pipes(stack)
            server_downward, client_downward = self._open_pipes(stack)

            def server_thread():
                from turingarena_impl.driver.server import run_server

                run_server(DriverProcessConnection(
                    upward=server_upward,
                    downward=server_downward,
                ), self.source_path, self.interface_path)

                logging.debug("driver server terminated")

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
    def _run_server_in_process(self):
        with subprocess.Popen(
                [
                    "python3",
                    "-m",
                    "turingarena_impl.driver.server",
                    self.source_path,
                    self.interface_path,
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
    def run(self, time_limit=None):
        with ExitStack() as stack:
            driver_connection = stack.enter_context(self._run_server_in_thread())

            process = Process(driver_connection)
            with process.run(time_limit=time_limit):
                try:
                    yield process
                except InterfaceExit:
                    pass
            process.stop()