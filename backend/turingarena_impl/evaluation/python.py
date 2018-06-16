import logging
import sys
from collections import namedtuple
from contextlib import ExitStack

from turingarena_impl.evaluation.segi import segi_subprocess
from turingarena_impl.evaluation.turingarena_tools import run_metaservers

logger = logging.getLogger(__name__)


class PythonEvaluator(namedtuple("PythonEvaluator", ["evaluator_path"])):
    """
    Evaluates a Python problem.
    """

    __slots__ = []

    def evaluate(self, submission):
        with ExitStack() as stack:
            env = stack.enter_context(run_metaservers())
            yield from segi_subprocess(submission, [
                sys.executable,
                "-u",
                self.evaluator_path,
            ], env=env)
