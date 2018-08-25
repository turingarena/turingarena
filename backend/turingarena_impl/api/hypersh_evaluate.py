import json
import os
import sys
import traceback
from tempfile import TemporaryDirectory

from turingarena_impl.api.aws_evaluate import cloud_evaluate
from turingarena_impl.api.dynamodb_events import store_events
from turingarena_impl.api.dynamodb_submission import load_submission
from turingarena_impl.cli_server.git_manager import GitManager


def do_evaluate():
    request_data = json.load(sys.stdin)

    submission_id = request_data["submission_id"]
    evaluation_id = request_data["evaluation_id"]
    evaluator_cmd = request_data["evaluator_cmd"]

    git = GitManager("/run/turingarena/db.git")
    git.init()

    for r in request_data["repositories"].values():
        git.fetch_repository(r)

    with TemporaryDirectory() as temp_dir:
        git.checkout_trees(request_data["packs"], temp_dir)

        os.chdir(temp_dir)
        submission = load_submission(submission_id)
        events = cloud_evaluate(submission, evaluator_cmd=evaluator_cmd)
        store_events(evaluation_id, events)


def main():
    try:
        do_evaluate()
    except Exception:
        # print the most useful stuff first (HyperSH crops the rest)
        print(traceback.format_exc()[-50:])
        raise


if __name__ == '__main__':
    main()
