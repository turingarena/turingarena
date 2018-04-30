import logging
import os
import signal
import subprocess
from abc import abstractmethod
from contextlib import contextmanager

from turingarena_impl.sandbox.processinfo import SandboxProcessInfo, ProcessStatus

logger = logging.Logger(__name__)


class Process:
    @abstractmethod
    def get_status(self, wait=False) -> SandboxProcessInfo:
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
        Process the status code of a process and return a tuple (status, error) where status is the process status
        and error is the eventual error message in case the process fails either with non zero return code or with a
        signal (for example is waited for exceeding time/memory limits or for trying to perform a blacklisted syscall).

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
            signal_number = os.WTERMSIG(status_code)
            signal_message = {
                signal.SIGXCPU: "CPU time limit exceeded",
                signal.SIGSEGV: "Segmentation fault",
                signal.SIGSYS: "Bad system call",
            }.get(signal_number, signal.Signals(signal_number).name)
            return ProcessStatus.TERMINATED_WITH_ERROR, f"Exited with signal {signal_number} ({signal_message})"
        assert False, "This should not be reached"

    def get_status(self, wait=False) -> SandboxProcessInfo:
        """
        Get information about a running process, such as status (RUNNING, TERMINATED),
        maximum memory utilization in bytes (maximum segment size, the maximum process lifetime memory utilization),
        user cpu time utilization (with milliseconds precision), and eventual error code information.

        If param wait is set, we wait for the process to terminate and then return the final resource
        utilization.

        Note: the memory usage is at least 20/30Mb even for small programs.

        This is due to the fact that Linux calculates the maximum segment size since the process creation (fork())
        and not since the effective program execution (exec()): after a fork the entire process address space is
        duplicated, so the new process MSS is as big as the MSS of the father process.

        Unfortunately there aren't simple workaround (or at least we didn't find any). But for processes that use more
        than 30Mb of memory the value is correct, so this shouldn't be a problem in most applications.
        """

        # if the process is already terminated, return the cached info
        if self.termination_info:
            return self.termination_info

        if not wait:
            # first send SIGSTOP to stop the process
            self.os_process.send_signal(signal.SIGSTOP)

        # then, use wait to get rusage struct (see man getrusage(2))
        _, exit_status, rusage = os.wait4(self.os_process.pid, 0 if wait else os.WUNTRACED)

        status, error = self.get_process_status_error(exit_status)
        info = SandboxProcessInfo(
            status=status,
            memory_usage=rusage.ru_maxrss * 1024,
            time_usage=rusage.ru_utime,
            error=error,
        )

        if status is ProcessStatus.RUNNING:
            assert not wait
            # if process is not terminated, restart it with a SIGCONT
            self.os_process.send_signal(signal.SIGCONT)
        else:
            self.termination_info = info

        return info


class CompilationFailedProcess(Process):
    def get_status(self, wait=False):
        return SandboxProcessInfo(
            status=ProcessStatus.TERMINATED_WITH_ERROR,
            memory_usage=0,
            time_usage=0.0,
            error=f"Compilation failed.",
        )
