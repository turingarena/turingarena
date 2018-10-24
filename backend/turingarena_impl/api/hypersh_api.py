import pickle
import sys
import traceback


def handle_generate_file(request):
    from turingarena_impl.api.s3_files import generate_cloud_files
    generate_cloud_files(request.working_directory)


def handle_evaluate(request):
    from turingarena_impl.api.dynamodb_events import store_events
    from turingarena_impl.evaluation.evaluate import evaluate

    request = pickle.load(sys.stdin.buffer)

    store_events(request.evaluation_id, evaluate(request.evaluate_request))


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
