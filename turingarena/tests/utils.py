from collections import deque

from turingarena.cli.loggerinit import init_logger
from turingarena.protocol.algorithm import load_algorithm

init_logger()


def callback_mock(calls, return_values=None):
    if return_values is not None:
        return_values = deque(return_values)

    def mock(*args):
        calls.append((mock, args))

        if return_values is not None:
            return return_values.popleft()

    return mock


def define_algorithms(interface_text, sources):
    for language, source in sources.items():
        with load_algorithm(
                source_text=source,
                language=language,
                interface_text=interface_text,
        ) as impl:
            yield impl
