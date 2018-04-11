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
    TERMINATED_WITH_ERROR = 2


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
        yield PopenProcess(*args, **kwargs)

    def __init__(self, *args, **kwargs):
        self.os_process = subprocess.Popen(*args, **kwargs)
        self.termination_info = None

    @staticmethod
    def get_process_status_error(status_code: int) -> (ProcessStatus, str):
        """
        Process the return code of a process and return a tuple (status, error) where status is the process status
        and error is the eventual error message in case the process fails either with non zero return code or with a
        signal.

        See man wait(2) for more info.
        """

        if os.WIFSTOPPED(status_code):
            return ProcessStatus.RUNNING, None
        if os.WIFEXITED(status_code):
            exit_code = os.WEXITSTATUS(status_code)
            if exit_code == 0:
                return ProcessStatus.TERMINATED_SUCCESSFULLY, None
            else:
                return ProcessStatus.TERMINATED_WITH_ERROR, f"Exited with status {exit_code}"
        if os.WIFSIGNALED(status_code):
            return ProcessStatus.TERMINATED_WITH_ERROR, f"Exited with signal {os.WTERMSIG(status_code)}"
        assert False, "This should not be reached"

    def get_status(self, wait_termination=False) -> ProcessInfo:
        """
        Get information about a running process, such as status (RUNNING, TERMINATED),
        maximum memory utilization in bytes (maximum segment size), user cpu time utilization
        (with milliseconds precision), and eventual error code information.

        Note: the memory usage is 20/30Mb even for small programs. This is due to the fact that Linux calculates the
        maximum segment size since the process creation (fork()) and not since the exec(): after a fork the entire
        process address space is duplicated, and so the initial MSS is as big as the mss of the father process at the
        moment of child creation. Unfortunately there aren't simple workaround (or at least we didn't find any).

        But process that uses more than 30Mb of memory the calculation is precise, so this shouldn't be a problem in
        most applications.

        If param wait_termination is set, we wait for the process to terminate and then return the final resource
        utilization. 
        """

        # if the process is already terminated, return the cached info
        if self.termination_info:
            return self.termination_info

        # first send SIGSTOP to stop the process
        if not wait_termination:
            self.os_process.send_signal(signal.SIGSTOP)

        # then, use wait to get rusage struct (see man getrusage(2))
        _, exit_status, rusage = os.wait4(self.os_process.pid, 0 if wait_termination else os.WUNTRACED)

        status, error = self.get_process_status_error(exit_status)
        info = ProcessInfo(
            status=status,
            memory_usage=rusage.ru_maxrss * 1024,
            time_usage=rusage.ru_utime,
            error=error,
        )

        if status is ProcessStatus.RUNNING:
            # if process is not terminated, restart it with a SIGCONT
            self.os_process.send_signal(signal.SIGCONT)
        else:
            self.termination_info = info

        return info

