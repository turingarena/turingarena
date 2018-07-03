import json
import logging
import os
import subprocess
import sys
import traceback
from tempfile import TemporaryDirectory

from turingarena_impl.api.aws_evaluate import cloud_evaluate
from turingarena_impl.api.dynamodb_events import store_events
from turingarena_impl.api.dynamodb_submission import load_submission


def do_evaluate():
    request_data = json.load(sys.stdin)

    submission_id = request_data["submission_id"]
    evaluation_id = request_data["evaluation_id"]
    evaluator_cmd = request_data["evaluator_cmd"]

    for r in request_data["repositories"].values():
        assert r["type"] == "git_clone"
        url = r["url"]
        branch = r["branch"]
        depth = r["depth"]

        if depth is not None:
            depth_options = [f"--depth={depth}"]
        else:
            depth_options = []

        if branch is not None:
            branch_options = [branch]
        else:
            branch_options = []

        cmd = [
            "git",
            "fetch",
            "--recurse-submodules=yes",
            *depth_options,
            url,
            *branch_options,
        ]
        logging.info(f"running {cmd}")
        subprocess.run(cmd, check=True)

    with TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)
        for p in request_data["packs"]:
            cmd = [
                "git",
                "read-tree",
                p,
            ]
            subprocess.run(cmd, check=True)
            cmd = [
                "git",
                f"--work-tree={temp_dir}",
                "checkout-index",
                "--all",
            ]
            subprocess.run(cmd, check=True)

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
