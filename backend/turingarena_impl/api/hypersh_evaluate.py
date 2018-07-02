import json
import sys
import traceback

from turingarena_impl.api.aws_evaluate import cloud_evaluate
from turingarena_impl.api.dynamodb_submission import load_submission


def do_evaluate():
    request_data = json.load(sys.stdin)

    submission_id = request_data["submission_id"]
    evaluator_cmd = request_data["evaluator_cmd"]

    submission = load_submission(submission_id)
    for event in cloud_evaluate(submission, evaluator_cmd=evaluator_cmd):
        print(event)


def main():
    try:
        do_evaluate()
    except Exception:
        traceback.print_exc(file=sys.stdout, limit=1)


if __name__ == '__main__':
    main()
