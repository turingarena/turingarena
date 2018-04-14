import json
import logging
import os
from collections import namedtuple
from contextlib import redirect_stdout
from io import StringIO
from tempfile import TemporaryDirectory

from turingarena.algorithm import Algorithm
from turingarena.loader import split_module, find_package_path
from turingarena.problem.evaluation import Evaluation
from turingarena.sandbox.languages.language import Language

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

    def evaluate(self, source_name, *, language=None):
        if language is None:
            language = Language.from_source_name(source_name)

        mod, arg = split_module(self.name)
        assert arg is None

        eval_stdout = StringIO()
        with redirect_stdout(eval_stdout):
            with TemporaryDirectory() as temp_dir:
                result_path = os.path.join(temp_dir, "result.json")
                script_path = find_package_path(mod, "evaluate.py")

                os.environ["submission_algorithm_source"] = source_name
                os.environ["submission_algorithm_language"] = language.name
                os.environ["result_path"] = result_path
                try:
                    with open(script_path) as f:
                        code = compile(f.read(), script_path, "exec")
                    script_globals = {}
                    exec(code, script_globals)
                    data = self.compat_evaluate(script_globals, language, source_name)
                finally:
                    del os.environ["submission_algorithm_source"]
                    del os.environ["submission_algorithm_language"]
                    del os.environ["result_path"]
                if os.path.exists(result_path):
                    assert data is None
                    with open(result_path) as f:
                        data = json.load(f)

        return Evaluation(
            stdout=eval_stdout.getvalue().splitlines(),
            data=data,
        )

    def compat_evaluate(self, script_globals, language, source_name):
        """For compatibility with problems defining evaluate(algorithm)"""
        if "evaluate" in script_globals:
            algorithm = Algorithm(
                source_name=source_name,
                language_name=language.name,
                interface_name=self.interface_name,
            )
            return script_globals["evaluate"](algorithm)
