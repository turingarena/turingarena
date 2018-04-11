import logging
import os
import signal
from abc import abstractmethod
from collections import namedtuple
from contextlib import contextmanager
from subprocess import TimeoutExpired

from turingarena.sandbox.exceptions import AlgorithmRuntimeError

logger = logging.getLogger(__name__)


class AlgorithmExecutable(namedtuple("AlgorithmExecutable", [
    "algorithm_dir",
    "language",
])):
    __slots__ = []

    @staticmethod
    def load(algorithm_dir):
        from turingarena.sandbox.languages.language import Language

        with open(os.path.join(algorithm_dir, "language.txt")) as f:
            language = Language.from_name(f.read().strip())

        return language.executable(
            algorithm_dir=algorithm_dir,
            language=language,
        )

    @staticmethod
    def _wait_or_send(process, which_signal):
        logger.debug(f"waiting for process pid = {process.pid} ...")
        try:
            process.wait(timeout=1.0)
        except TimeoutExpired:
            logger.warning(f"timeout expired! sending signal {which_signal}")
            process.send_signal(which_signal)

    @contextmanager
    def manage_process(self, process):
        logger.debug(f"starting process")
        with process:
            try:
                yield process
            finally:
                self._wait_or_send(process, signal.SIGQUIT)
                self._wait_or_send(process, signal.SIGKILL)

            logger.debug(f"process {process.pid} terminated")

            if process.returncode != 0:
                logger.warning(f"process terminated with returncode {process.returncode}")
                raise AlgorithmRuntimeError(f"invalid return code {process.returncode}")

    @staticmethod
    def get_rusage(process):
        # check if process already terminated
        if process.poll():
            return None

        # To get precise resource utilization we send a stop signal the process, than use wait4 to get rusage,
        # and then send a continue signal. This is done because in Linux you can't get precise CPU time
        # utilization from /proc or other methods that you can use when the process is running.
        try:
            logger.debug(f"Sending SIGSTOP to pid = {process.pid}")
            process.send_signal(signal.SIGSTOP)
            logger.debug(f"Waiting pid = {process.pid}")
            rusage = os.wait4(process.pid, os.WUNTRACED)[2]
            logger.debug(f"Sending SIGCONT to pid = {process.pid}")
            process.send_signal(signal.SIGCONT)
            return rusage
        except ChildProcessError:
            return None

    def get_time_usage(self, process):
        rusage = self.get_rusage(process)
        return rusage.ru_utime if rusage else 0

    def get_memory_usage(self, process):
        rusage = self.get_rusage(process)
        return rusage.ru_maxrss if rusage else 0

    @abstractmethod
    def run(self, connection):
        pass
