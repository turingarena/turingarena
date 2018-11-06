import os
from tempfile import TemporaryDirectory

from turingarena.api.commands import EvaluateRequest
from turingarena.api.git_manager import create_working_directory
from turingarena.evaluation.evaluator import Evaluator


def cloud_evaluate(evaluate_request: EvaluateRequest, reset_env=False):
    with TemporaryDirectory() as temp_dir:
        files = {}
        for name, submission_file in evaluate_request.submission.items():
            dirpath = os.path.join(temp_dir, name)
            os.mkdir(dirpath)
            path = os.path.join(dirpath, submission_file.filename)
            with open(path, "xb") as f:
                f.write(submission_file.content)
            files[name] = path

        with create_working_directory(evaluate_request.working_directory) as work_dir:
            cwd = os.path.join(work_dir, evaluate_request.working_directory.current_directory)
            yield from Evaluator(cwd).evaluate(files=files, seed=evaluate_request.seed, reset_env=reset_env)
