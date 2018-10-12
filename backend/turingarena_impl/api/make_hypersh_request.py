import pickle
import sys

from turingarena_common.commands import WorkingDirectory, Pack, GitRepository
from turingarena_impl.api.request import CloudEvaluateRequest

pickle.dump(CloudEvaluateRequest(
    working_directory=WorkingDirectory(
        pack=Pack(
            commit_oid=["4f209f1b16bf778a8d678156aba6aae320f979c3"],
            repositories=[
                GitRepository(
                    url="https://github.com/turingarena/turingarena.git",
                    branch=None,
                    depth=None,
                )
            ]
        ),
        current_directory=".",
    ),
    submission_id=sys.argv[1],
    evaluation_id="test_evaluation",
    evaluator="/usr/local/bin/python -u evaluator.py",
), sys.stdout.buffer)
