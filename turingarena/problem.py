import importlib
import os
import sys
from tempfile import TemporaryDirectory

from turingarena.cli import docopt_cli
from turingarena.protocol.algorithm import Algorithm
from turingarena.protocol.model.model import InterfaceDefinition
from turingarena.sandbox.sources import load_source


@docopt_cli
def problem_evaluate_cli(args):
    """TuringArena problem evaluator.

    Usage:
        evaluate [options]

    Options:
        -x --language=<lang>  Source language [default: c++].
        -I --interface=<file>  Interface definition file [default: interface.txt].
        -C --checker=<c>  Python module where the checker is located [default: problem:checker]
    """

    checker_module_name, checker_attr_name = args["--checker"].split(":")
    checker_module = importlib.import_module(checker_module_name)
    checker = getattr(checker_module, checker_attr_name)

    with open(args["--interface"]) as f:
        interface_text = f.read()

    interface = InterfaceDefinition.compile(interface_text)
    source = load_source(
        sys.stdin.read(),
        language=args["--language"],
        interface=interface,
    )

    with TemporaryDirectory(dir="/dev/shm") as temp_dir:
        algorithm_dir = os.path.join(temp_dir, "algorithm")
        source.compile(algorithm_dir=algorithm_dir)

        checker(Algorithm(algorithm_dir=algorithm_dir, interface=interface))
