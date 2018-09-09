import pickle
import sys
import traceback

from turingarena_impl.api.dynamodb_events import store_events
from turingarena_impl.api.dynamodb_submission import load_submission
from turingarena_impl.api.request import CloudEvaluateRequest, CloudGenerateFileRequest
from turingarena_impl.api.s3_files import generate_cloud_files
from turingarena_impl.evaluation.evaluate import evaluate


def handle_generate_file(request: CloudGenerateFileRequest):
    generate_cloud_files(request.working_directory)


def handle_evaluate(request: CloudEvaluateRequest):
    events = evaluate(
        working_directory=request.working_directory,
        evaluator_cmd=request.evaluator,
        submission=load_submission(request.submission_id),
    )

    store_events(request.evaluation_id, events)


def handle(request):
    for t, handler in REQUEST_MAP.items():
        if isinstance(request, t):
            return handler(request)


def execute_request():
    request = pickle.load(sys.stdin.buffer)
    handle(request)


REQUEST_MAP = {
    CloudEvaluateRequest: handle_evaluate,
    CloudGenerateFileRequest: handle_generate_file,
}


def main():
    try:
        execute_request()
    except Exception:
        # print the most useful stuff first (HyperSH crops the rest)
        print(traceback.format_exc()[-50:])
        raise


if __name__ == '__main__':
    main()
