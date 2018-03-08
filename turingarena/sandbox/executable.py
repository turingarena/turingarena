import logging
import signal
from abc import abstractmethod
from subprocess import TimeoutExpired

import psutil
from decorator import contextmanager

from turingarena.common import ImmutableObject
from turingarena.sandbox.exceptions import AlgorithmRuntimeError

logger = logging.getLogger(__name__)


class AlgorithmExecutable(ImmutableObject):
    __slots__ = [
        "algorithm_dir",
        "language",
        "interface",
    ]

    def _wait_or_send(self, process, which_signal):
        logger.debug(f"waiting for process...")
        try:
            process.wait(timeout=1.0)
        except TimeoutExpired:
            logger.debug(f"timeout expired! sending signal {which_signal}")
            process.send_signal(which_signal)

    @contextmanager
    def manage_process(self, process, get_stack_trace=None):
        logger.debug(f"starting process")
        with process:
            try:
                yield process
            finally:
                self._wait_or_send(process, signal.SIGQUIT)
                self._wait_or_send(process, signal.SIGKILL)

            if process.returncode != 0:
                if get_stack_trace is not None:
                    st = get_stack_trace()
                else:
                    st = ""

                logger.warning(f"process terminated with returncode {process.returncode}")
                raise AlgorithmRuntimeError(
                    f"invalid return code {process.returncode}",
                    st,
                )

    def get_time_usage(self, process):
        time_usage = psutil.Process(process.pid).cpu_times().user
        logger.debug(f"time usage of PID {process.pid} == {time_usage}")
        return time_usage

    def get_memory_usage(self, process):
        memory_usage = psutil.Process(process.pid).memory_full_info().vms
        logger.debug(f"memory usage of PID {process.pid} == {memory_usage}")
        return memory_usage

    def get_stack_trace(self, process):
        bt = self.get_back_trace(executable_filename, cwd)

    @abstractmethod
    def run(self, connection):
        pass
