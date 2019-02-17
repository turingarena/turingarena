import pickle
import sys
import traceback

from turingarena_cloud.hypersh_evaluate import handle_evaluate
from turingarena_cloud.hypersh_files import handle_generate_file
from turingarena_cloud.request import CloudEvaluateRequest, CloudGenerateFileRequest


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
        # print the most useful stuff to stderr (HyperSH crops the rest in logs)
        print(traceback.format_exc()[-50:], file=sys.stderr)
        # print the full stack trace to stdout (for use with 'hyper func get <call-id>')
        traceback.print_exc(file=sys.stdout)

        raise


if __name__ == '__main__':
    main()
