import os
from tempfile import TemporaryDirectory

from turingarena.evaluation.evaluator import Evaluator
from turingarena_cloud.commands import EvaluateRequest
from turingarena_cloud.git_manager import create_working_directory


def cloud_evaluate(evaluate_request: EvaluateRequest):
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
            evaluator_dir = os.path.join(
                work_dir,
                evaluate_request.working_directory.current_directory,
            )

            yield from Evaluator(evaluator_dir).evaluate(
                files,
                seed=evaluate_request.seed,
            )
