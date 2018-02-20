import os
import random
import string
import sys
from collections import deque
from contextlib import contextmanager
from tempfile import TemporaryDirectory

from turingarena.protocol.client import ProxiedAlgorithm
from turingarena.protocol.module import ProtocolSource
from turingarena.sandbox.algorithm import Algorithm
from turingarena.sandbox.cpp import CppAlgorithmSource
from turingarena.sandbox.python import PythonAlgorithmSource


@contextmanager
def cpp_implementation(protocol_text, source_text, interface_name):
    protocol_name = "test_protocol_" + ''.join(random.choices(string.ascii_lowercase, k=8))
    protocol_source = ProtocolSource(
        text=protocol_text,
        filename="<none>",
    )

    algorithm_source = CppAlgorithmSource(
        filename=None,
        language="c++",
        text=source_text,
        protocol_name=protocol_name,
        interface_name=interface_name,
    )

    with TemporaryDirectory() as temp_dir:
        protocol_source.generate(dest_dir=temp_dir, name=protocol_name)

        sys.path.append(temp_dir)
        old_path = os.environ["PYTHONPATH"]
        try:
            os.environ["PYTHONPATH"] = temp_dir

            algorithm_dir = os.path.join(temp_dir, "algorithm")
            algorithm_executable = algorithm_source.compile(algorithm_dir=algorithm_dir)
            algorithm = Algorithm(source=algorithm_source, executable=algorithm_executable)

            impl = ProxiedAlgorithm(
                algorithm=algorithm,
            )
            yield impl
        finally:
            sys.path.remove(temp_dir)
            os.environ["PYTHONPATH"] = old_path

@contextmanager
def python_implementation(protocol_text, source_text, interface_name):
    protocol_name = "test_protocol_" + ''.join(random.choices(string.ascii_lowercase, k=8))
    protocol_source = ProtocolSource(
        text=protocol_text,
        filename="<none>",
    )

    algorithm_source = PythonAlgorithmSource(
        filename=None,
        language="python",
        text=source_text,
        protocol_name=protocol_name,
        interface_name=interface_name,
    )

    with TemporaryDirectory() as temp_dir:
        protocol_source.generate(dest_dir=temp_dir, name=protocol_name)

        sys.path.append(temp_dir)
        old_path = os.environ["PYTHONPATH"]
        try:
            os.environ["PYTHONPATH"] = temp_dir

            algorithm_dir = os.path.join(temp_dir, "algorithm")
            algorithm_executable = algorithm_source.compile(algorithm_dir=algorithm_dir)
            algorithm = Algorithm(source=algorithm_source, executable=algorithm_executable)

            impl = ProxiedAlgorithm(
                algorithm=algorithm,
            )
            yield impl
        finally:
            sys.path.remove(temp_dir)
            os.environ["PYTHONPATH"] = old_path

def callback_mock(calls, return_values=None):
    if return_values is not None:
        return_values = deque(return_values)

    def mock(*args):
        calls.append((mock, args))

        if return_values is not None:
            return return_values.popleft()

    return mock
