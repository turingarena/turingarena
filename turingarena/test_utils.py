import os
from collections import deque
from contextlib import contextmanager
from tempfile import TemporaryDirectory

from turingarena.cli.loggerinit import init_logger
from turingarena.protocol.algorithm import Algorithm
from turingarena.protocol.model.model import InterfaceDefinition
from turingarena.sandbox.sources import load_source

init_logger()


@contextmanager
def define_interface(text):
    interface = InterfaceDefinition.compile(text)
    yield interface


@contextmanager
def define_algorithm(*, interface, language, source_text):
    algorithm_source = load_source(source_text, interface=interface, language=language)

    with TemporaryDirectory(dir="/dev/shm") as temp_dir:
        algorithm_dir = os.path.join(temp_dir, "algorithm")
        algorithm_source.compile(algorithm_dir)

        yield Algorithm(
            algorithm_dir=algorithm_dir,
            interface=interface,
        )


def callback_mock(calls, return_values=None):
    if return_values is not None:
        return_values = deque(return_values)

    def mock(*args):
        calls.append((mock, args))

        if return_values is not None:
            return return_values.popleft()

    return mock


def define_many(interface_text, sources):
    with define_interface(interface_text) as interface:
        for language, source in sources.items():
            with define_algorithm(
                    source_text=source,
                    language=language,
                    interface=interface,
            ) as impl:
                yield impl
