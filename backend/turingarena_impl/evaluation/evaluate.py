from contextlib import ExitStack

from turingarena_impl.evaluation.segi import segi_subprocess
from turingarena_impl.evaluation.turingarena_tools import run_metaservers


def evaluate(files, *, evaluator_cmd):
    with ExitStack() as stack:
        env = stack.enter_context(run_metaservers())
        evaluation = segi_subprocess(
            files,
            evaluator_cmd,
            shell=True,
            env=env,
        )

        for event in evaluation:
            yield event
