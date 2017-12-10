from contextlib import contextmanager
from tempfile import TemporaryDirectory

from turingarena.protocol.client import ProxiedAlgorithm
from turingarena.sandbox.algorithm import Algorithm
from turingarena.sandbox.cpp import CppAlgorithmSource


@contextmanager
def cpp_implementation(source_text, protocol_name, interface_name):
    algorithm_source = CppAlgorithmSource(
        filename=None,
        language="c++",
        text=source_text,
        protocol_name=protocol_name,
        interface_name=interface_name,
    )

    with TemporaryDirectory() as temp_dir:
        algorithm_executable = algorithm_source.compile(name=interface_name, dest_dir=temp_dir)
        algorithm = Algorithm(source=algorithm_source, executable=algorithm_executable)

        impl = ProxiedAlgorithm(
            algorithm=algorithm,
        )

        yield impl
