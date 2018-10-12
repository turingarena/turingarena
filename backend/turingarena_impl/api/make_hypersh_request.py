import pickle
import sys

from turingarena_common.commands import WorkingDirectory, Pack, GitRepository
from turingarena_impl.api.request import CloudEvaluateRequest

pickle.dump(CloudEvaluateRequest(
    working_directory=WorkingDirectory(
        pack=Pack(
            parts=["d1a18623594c47621e9289767bc3ce997ce45756"],
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
