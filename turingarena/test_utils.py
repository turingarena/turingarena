import os
import random
import string
from collections import deque
from contextlib import contextmanager
from tempfile import TemporaryDirectory

from turingarena.protocol.module import InterfaceSource
from turingarena.protocol.proxy import ProxiedAlgorithm
from turingarena.sandbox.languages.cpp import CppAlgorithmSource
from turingarena.sandbox.languages.python import PythonAlgorithmSource


@contextmanager
def define_interface(text):
    interface = "test_interface_" + ''.join(random.choices(string.ascii_lowercase, k=8))
    source = InterfaceSource(text)
    with TemporaryDirectory() as temp_dir:
        source.generate(
            name=interface,
            dest_dir=temp_dir,
        )

        old_path = os.environ.get("TURINGARENA_INTERFACE_PATH")
        try:
            os.environ["TURINGARENA_INTERFACE_PATH"] = temp_dir
            yield interface
        finally:
            if old_path is not None:
                os.environ["TURINGARENA_INTERFACE_PATH"] = old_path


@contextmanager
def define_algorithm(*, interface, language, source_text):
    languages = {
        "c++": CppAlgorithmSource,
        "python": PythonAlgorithmSource,
    }

    algorithm_source = languages[language](
        interface=interface,
        filename=None,
        language=language,
        text=source_text,
    )

    with TemporaryDirectory() as temp_dir:
        algorithm_dir = os.path.join(temp_dir, "algorithm")
        algorithm_source.compile(algorithm_dir)

        yield ProxiedAlgorithm(
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
