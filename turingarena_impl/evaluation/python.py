import json
import logging
import os
import runpy
from collections import namedtuple
from contextlib import redirect_stdout, ExitStack
from io import StringIO
from tempfile import TemporaryDirectory

from turingarena_impl.evaluation.environ import env_extension
from turingarena_impl.evaluation.segi import submission_environ
from turingarena_impl.evaluation.turingarena_tools import run_metaservers
from turingarena_impl.loader import find_package_path

logger = logging.getLogger(__name__)


class HostPythonEvaluator(namedtuple("HostPythonEvaluator", ["name"])):
    """
    Evaluates a Python problem in the host interpreter.
    Stdout is captured by changing sys.stdout.
    """

    __slots__ = []

    def evaluate(self, source_path, *, language_name=None):
        eval_stdout = StringIO()
        with ExitStack() as stack:
            stack.enter_context(redirect_stdout(eval_stdout))
            temp_dir = stack.enter_context(TemporaryDirectory())
            result_path = os.path.join(temp_dir, "result.json")

            script_path = find_package_path(self.name, "evaluate.py")

            stack.enter_context(run_metaservers())

            interface_rel_path = os.path.join(os.path.dirname(script_path), "interface.txt")

            stack.enter_context(env_extension(
                turingarena_default_interface=f":{interface_rel_path}",
                problem_name=self.name
            ))

            stack.enter_context(submission_environ(dict(
                source=source_path,
                source_language=language_name,
            )))

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
