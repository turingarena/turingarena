import json
import logging
import os
import runpy
from collections import namedtuple
from contextlib import redirect_stdout, contextmanager, ExitStack
from io import StringIO
from tempfile import TemporaryDirectory

from turingarena_impl.interface.driver import DriverServer
from turingarena_impl.loader import split_module, find_package_path
from turingarena_impl.problem.evaluation import Evaluation
from turingarena_impl.sandbox.server import SandboxServer

logger = logging.getLogger(__name__)


class HostPythonEvaluator(namedtuple("HostPythonEvaluator", [
    "name",
    "interface_name",
])):
    """
    Evaluates a Python problem in the host interpreter.
    Stdout is captured by changing sys.stdout.
    """

    __slots__ = []

    def evaluate(self, source_name, *, language_name=None):
        mod, arg = split_module(self.name)
        assert arg is None

        eval_stdout = StringIO()
        with ExitStack() as stack:
            stack.enter_context(redirect_stdout(eval_stdout))
            temp_dir = stack.enter_context(TemporaryDirectory())
            result_path = os.path.join(temp_dir, "result.json")
            script_path = find_package_path(mod, "evaluate.py")

            sandbox_dir = stack.enter_context(SandboxServer.run())
            driver_dir = stack.enter_context(DriverServer.run())

            stack.enter_context(env_extension(
                TURINGARENA_SANDBOX_DIR=sandbox_dir,
                TURINGARENA_DRIVER_DIR=driver_dir,
                submission_algorithm_source=source_name,
                submission_algorithm_language=language_name,
                result_path=result_path,
                problem_name=self.name
            ))

            runpy.run_path(script_path)

            if os.path.exists(result_path):
                with open(result_path) as f:
                    data = json.load(f)
            else:
                data = None

        return Evaluation(
            stdout=eval_stdout.getvalue().splitlines(),
            data=data,
        )


@contextmanager
def env_extension(**d):
    for k in d:
        assert k not in os.environ
        if d[k] is not None:
            os.environ[k] = d[k]
    try:
        yield
    finally:
        for k in d:
            if d[k] is not None:
                del os.environ[k]
