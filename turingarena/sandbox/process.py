import subprocess
import signal
import os
import logging

from collections import namedtuple
from contextlib import contextmanager
from abc import abstractmethod
from enum import Enum


logger = logging.Logger(__name__)


class ProcessStatus(Enum):
    RUNNING = 0
    TERMINATED_SUCCESSFULLY = 1
    TERMINATED_ERROR = 2


ProcessInfo = namedtuple("ProcessInfo", [
    "status",
    "memory_usage",
    "time_usage",
    "error",
])


class Process:

    @abstractmethod
    def get_status(self, wait_termination=False) -> ProcessInfo:
        pass


class PopenProcess(Process):
    @staticmethod
    @contextmanager
    def run(*args, **kwargs):
        logger.debug("Starting process")
        yield PopenProcess(*args, **kwargs)
        logger.debug("Process terminated")

    def __init__(self, *args, **kwargs):
        self.os_process = subprocess.Popen(*args, **kwargs)
        self.termination_info = None

    @staticmethod
    def get_process_status_error(status_code: int) -> (ProcessStatus, str):
        if os.WIFSTOPPED(status_code):
            return ProcessStatus.RUNNING, None
        if os.WIFEXITED(status_code):
            exit_code = os.WEXITSTATUS(status_code)
            if exit_code == 0:
                return ProcessStatus.TERMINATED_SUCCESSFULLY, None
            else:
                return ProcessStatus.TERMINATED_ERROR, f"Exited with status {exit_code}"
        if os.WIFSIGNALED(status_code):
            return ProcessStatus.TERMINATED_ERROR, f"Exited with signal {os.WTERMSIG(status_code)}"
        assert False, "This should not be reached"

    def get_status(self, wait_termination=False) -> ProcessInfo:
        if self.termination_info:
            return self.termination_info
        self.os_process.send_signal(signal.SIGSTOP)
        _, exit_status, rusage = os.wait4(self.os_process.pid, 0 if wait_termination else os.WUNTRACED)
        status, error = self.get_process_status_error(exit_status)

        info = ProcessInfo(
            status=status,
            memory_usage=rusage.ru_maxrss,
            time_usage=rusage.ru_utime,
            error=error,
        )

        if status is ProcessStatus.RUNNING:
            self.os_process.send_signal(signal.SIGCONT)
        else:
            self.termination_info = info
        return info

