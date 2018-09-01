import subprocess
import sys
from contextlib import ExitStack

from turingarena_common.commands import LocalExecutionParameters, EvaluateCommandParameters
from turingarena_impl.evaluation.evaluate import evaluate


def evaluate_cmd(parameters: EvaluateCommandParameters, local_execution: LocalExecutionParameters):
    with ExitStack() as stack:
        output = sys.stdout

        if not parameters.raw_output:
            jq = stack.enter_context(subprocess.Popen(
                ["jq", "-j", "--unbuffered", ".payload"],
                stdin=subprocess.PIPE,
                universal_newlines=True,
            ))
            output = jq.stdin

        for event in evaluate(
                working_directory=parameters.working_directory,
                evaluator_cmd=parameters.evaluator,
                submission=parameters.submission,
                local_execution=local_execution,
        ):
            print(event, file=output, flush=True)
