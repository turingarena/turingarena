import logging
import os
import signal
import subprocess
import time

from turingarena.driver.client.processinfo import SandboxProcessInfo
from turingarena.driver.sandbox.connection import SandboxProcessConnection, ProcessManager


def create_popen_process_connection(*args, **kwargs):
    p = subprocess.Popen(
        *args,
        **kwargs,
        universal_newlines=True,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        bufsize=1,
    )
    return SandboxProcessConnection(
        downward=p.stdin,
        upward=p.stdout,
        manager=PopenProcessManager(p),
    )


class PopenProcessManager(ProcessManager):
    def __init__(self, os_process):
        self.os_process = os_process
        self.termination_info = None

    def get_connection(self):
        return

    @staticmethod
    def _get_process_termination_message(status_code: int):
        """
        ProcessManager the status code of a process and return a tuple (status, error) where status is the process status
        and error is the eventual error message in case the process fails either with non zero return code or with a
        signal (for example is waited for exceeding time/memory limits or for trying to perform a blacklisted syscall).

        See man wait(2) for more info.
        """

        if os.WIFSTOPPED(status_code):
            return None
        if os.WIFEXITED(status_code):
            exit_code = os.WEXITSTATUS(status_code)
            if exit_code == 0:
                return f"exited normally"
            else:
                return f"exited with status {exit_code}"
        if os.WIFSIGNALED(status_code):
            signal_number = os.WTERMSIG(status_code)
            signal_name = signal.Signals(signal_number).name
            signal_message = {
                signal.SIGSEGV: "Segmentation fault",
                signal.SIGSYS: "Bad system call",
            }.get(signal_number, None)
            if signal_message is not None:
                signal_explaination = f"{signal_name} - {signal_message}"
            else:
                signal_explaination = f"{signal_name}"
            return f"interrupted by signal {signal_number} - {signal_explaination}"
        assert False, "This should not be reached"

    def _read_proc_stat(self):
        with open(f"/proc/{self.os_process.pid}/stat") as f:
            line = f.read()

        pid, line = line.split(maxsplit=1)

        # safely strip cmd fields:
        # see https://gitlab.com/procps-ng/procps/blob/b3b7a35050e29317fa66be4535aeaf83acbdc946/proc/readproc.c#L606
        lookup = ") "
        lookup_index = line.rindex(lookup) + len(lookup)
        cmd = line[:lookup_index]

        line = line[lookup_index:]
        return [pid, cmd, *line.split()]

    def _wait_for_interruptible(self):
        timeout = 0.5
        trials = 10
        for trial in range(trials):
            status = self._read_proc_stat()[2]
            logging.error(f"ProcessManager status: {status}")
            if status in ("S", "Z"):
                break
            time.sleep(timeout / trials)
        else:
            logging.debug(f"ProcessManager did not reach interruptible state in {timeout} s")

    def _read_stat_resource_usage(self):
        fields = self._read_proc_stat()
        # see man 5 proc
        rss = int(fields[23]) * os.sysconf("SC_PAGE_SIZE")

        return rss

    def _reset_maxrss(self):
        os.system(f"echo 5 > /proc/{self.os_process.pid}/clear_refs")

        # fd = os.open(f"/proc/{self.os_process.pid}/clear_refs", os.O_WRONLY)
        # try:
        #    os.write(fd, b"5")
        # finally:
        #    os.close(fd)

    def _do_get_status(self, kill_reason):
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
        if self.termination_info is not None:
            return self.termination_info

        self._wait_for_interruptible()

        # first send SIGSTOP to stop the process
        self.os_process.send_signal(signal.SIGSTOP)

        # then, use wait to get rusage struct (see man getrusage(2))
        _, exit_status, rusage = os.wait4(self.os_process.pid, os.WUNTRACED)

        termination_message = self._get_process_termination_message(exit_status)
        running = termination_message is None

        if running:
            error = f"running normally"
            if kill_reason is not None:
                error += f", killed because: {kill_reason}"
        else:
            error = termination_message

        maxrss = rusage.ru_maxrss * 1024

        if running:
            rss = self._read_stat_resource_usage()
        else:
            rss = 0

        info = SandboxProcessInfo(
            peak_memory_usage=maxrss,
            current_memory_usage=rss,
            time_usage=rusage.ru_utime,
            error=error,
        )

        if running:
            if kill_reason is not None:
                logging.debug(f"killing process")
                self.os_process.send_signal(signal.SIGKILL)
                os.wait4(self.os_process.pid, 0)
                self.termination_info = info
            else:
                # if process is not terminated, restart it with a SIGCONT
                self.os_process.send_signal(signal.SIGCONT)
        else:
            self.termination_info = info

        return info
