import logging
from abc import abstractmethod

import psutil

from turingarena.common import ImmutableObject

logger = logging.getLogger(__name__)


class AlgorithmExecutable(ImmutableObject):
    __slots__ = [
        "algorithm_dir",
        "language",
        "interface",
    ]

    def get_time_usage(self, process):
        time_usage = psutil.Process(process.pid).cpu_times().user
        logger.debug(f"time usage of PID {process.pid} == {time_usage}")
        return time_usage

    def get_memory_usage(self, process):
        memory_usage = psutil.Process(process.pid).memory_full_info().vms
        logger.debug(f"memory usage of PID {process.pid} == {memory_usage}")
        return memory_usage

    @abstractmethod
    def run(self, connection):
        pass
