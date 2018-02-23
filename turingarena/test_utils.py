import os
import random
import string
import sys
from collections import deque
from contextlib import contextmanager
from tempfile import TemporaryDirectory

from turingarena.protocol.module import ProtocolSource
from turingarena.protocol.proxy.library import ProxiedAlgorithm
from turingarena.sandbox.languages.cpp import CppAlgorithmSource
from turingarena.sandbox.languages.python import PythonAlgorithmSource


@contextmanager
def define_protocol(text):
    protocol = "test_protocol_" + ''.join(random.choices(string.ascii_lowercase, k=8))
    source = ProtocolSource(text)
    with TemporaryDirectory() as temp_dir:
        source.generate(
            name=protocol,
            dest_dir=temp_dir,
        )

        sys.path.append(temp_dir)
        old_path = os.environ["PYTHONPATH"]
        try:
            os.environ["PYTHONPATH"] = temp_dir
            yield protocol
        finally:
            sys.path.remove(temp_dir)
            os.environ["PYTHONPATH"] = old_path


@contextmanager
def define_algorithm(*, protocol, language, source_text, interface_name):
    interface = f"{protocol}:{interface_name}"

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


def define_many(protocol_text, interface_name, sources):
    with define_protocol(protocol_text) as protocol:
        for language, source in sources.items():
            with define_algorithm(
                    source_text=source,
                    language=language,
                    protocol=protocol,
                    interface_name=interface_name,
            ) as impl:
                yield impl
