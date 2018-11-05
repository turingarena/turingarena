import os
from tempfile import TemporaryDirectory

from turingarena_common.commands import LocalExecutionParameters, EvaluateRequest
from turingarena_impl.cli_server.pack import create_working_directory
from turingarena_impl.evaluation.evaluator import Evaluator


def evaluate(evaluate_request: EvaluateRequest, local_execution=LocalExecutionParameters.DEFAULT, reset_env=False):
    with TemporaryDirectory() as temp_dir:
        files = {}
        for name, submission_file in evaluate_request.submission.items():
            dirpath = os.path.join(temp_dir, name)
            os.mkdir(dirpath)
            path = os.path.join(dirpath, submission_file.filename)
            with open(path, "xb") as f:
                f.write(submission_file.content)
            files[name] = path

        with create_working_directory(evaluate_request.working_directory, local_execution=local_execution) as work_dir:
            cwd = os.path.join(work_dir, evaluate_request.working_directory.current_directory)
            yield from Evaluator(cwd).evaluate(files=files, seed=evaluate_request.seed, reset_env=reset_env)
