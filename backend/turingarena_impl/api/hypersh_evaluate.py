import pickle
import sys
import traceback


def do_evaluate():
    from turingarena_impl.api.dynamodb_events import store_events
    from turingarena_impl.api.dynamodb_submission import load_submission
    from turingarena_impl.evaluation.evaluate import evaluate

    request = pickle.load(sys.stdin.buffer)

    events = evaluate(
        working_directory=request.working_directory,
        evaluator_cmd=request.evaluator,
        submission=load_submission(request.submission_id),
    )

    store_events(request.evaluation_id, events)


def main():
    try:
        do_evaluate()
    except Exception:
        # print the most useful stuff first (HyperSH crops the rest)
        print(traceback.format_exc()[-256:])
        raise


if __name__ == '__main__':
    main()
