import logging
import os
import subprocess
import sys
from contextlib import ExitStack
from tempfile import TemporaryDirectory

from turingarena_common.commands import LocalExecutionParameters, EvaluateCommandParameters
from turingarena_impl.cli_server.pack import enter_working_directory
from turingarena_impl.evaluation.evaluator import Evaluator


def evaluate_cmd(parameters: EvaluateCommandParameters, local_execution: LocalExecutionParameters):
    with ExitStack() as stack:
        stack.enter_context(enter_working_directory(
            parameters.working_directory,
            local_execution=local_execution,
        ))

        output = sys.stdout

        if not parameters.raw_output:
            jq = stack.enter_context(subprocess.Popen(
                ["jq", "-j", "--unbuffered", ".payload"],
                stdin=subprocess.PIPE,
                universal_newlines=True,
            ))
            output = jq.stdin

        files = {}
        with TemporaryDirectory() as temp_dir:
            for name, submission_file in parameters.submission.items():
                dirpath = os.path.join(temp_dir, name)
                os.mkdir(dirpath)
                path = os.path.join(dirpath, submission_file.filename)
                with open(path, "xb") as f:
                    f.write(submission_file.content)
                files[name] = path
            logging.info(f"Submission fields: {list(parameters.submission.keys())}")

            evaluator = Evaluator.get_evaluator(parameters.evaluator)
            logging.info(f"Running evaluator: {evaluator}")
            for event in evaluator.evaluate(files=files):
                print(event, file=output, flush=True)
