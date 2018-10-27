import pickle
import sys

from turingarena_common.commands import WorkingDirectory, Pack, GitRepository, EvaluateRequest
from turingarena_common.submission import SubmissionFile

from turingarena_impl.api.request import CloudEvaluateRequest

filename = sys.argv[1]

with open(filename) as f:
    content = f.read()

pickle.dump(CloudEvaluateRequest(
    evaluation_id="test_evaluation",
    evaluate_request=EvaluateRequest(
        submission={
            "source", SubmissionFile(filename, content),
        },
        working_directory=WorkingDirectory(
            pack=Pack(
                oid="4f209f1b16bf778a8d678156aba6aae320f979c3",
                repository=GitRepository(
                    url="https://github.com/turingarena/turingarena.git",
                    branch=None,
                    depth=None,
                ),
            ),
            current_directory="examples/sum_of_two_numbers",
        ),
        seed=None,
    ),
), sys.stdout.buffer)
