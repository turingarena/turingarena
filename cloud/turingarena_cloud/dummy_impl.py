from http import HTTPStatus

from turingarena_cloud.common import ProxyError

DUMMY_SUBMISSION_ID = "dummy_submission_id"


def do_evaluate(params):
    source_field_name = "submission[source]"
    try:
        source = params[source_field_name].value
    except KeyError:
        raise ProxyError(HTTPStatus.BAD_REQUEST, dict(message=f"Missing field '{source_field_name}'"))

    if not isinstance(source, bytes):
        raise ProxyError(HTTPStatus.BAD_REQUEST, dict(message=f"Field '{source_field_name}' is not a file"))

    return dict(
        id=DUMMY_SUBMISSION_ID,
    )


def do_evaluation_events(params):
    try:
        evaluation_id = params["evaluation"]
    except KeyError:
        raise ProxyError(HTTPStatus.BAD_REQUEST, dict(message=f"Missing parameter 'evaluation'"))
    if evaluation_id != "dummy_submission_id":
        raise ProxyError(HTTPStatus.NOT_FOUND, dict(message=f"Evaluation does not exist '{evaluation_id}'"))
    after = params.get("after", None)
    if after is None:
        return dict(
            begin=None,
            end="cursor_1",
            data=[
                dict(type="text", payload="Evaluating..."),
                dict(type="text", payload="\n"),
            ],
        )
    elif after == "cursor_1":
        return dict(
            begin="cursor_1",
            end="cursor_2",
            data=[
                dict(type="text", payload="Evaluating subtask 1..."),
                dict(type="text", payload="\n"),
                dict(type="text", payload="Subtask 1 passed!"),
                dict(type="text", payload="\n"),
                dict(type="data", payload=dict(type="score", score=20, max_score=20)),
            ],
        )
    elif after == "cursor_2":
        return dict(
            begin="cursor_2",
            end=None,
            data=[
                dict(type="text", payload="Evaluating subtask 2..."),
                dict(type="text", payload="\n"),
                dict(type="text", payload="Subtask 2 failed."),
                dict(type="text", payload="\n"),
                dict(type="data", payload=dict(type="score", score=0, max_score=80)),
            ],
        )
    else:
        raise ProxyError(HTTPStatus.NOT_FOUND, dict(message=f"Invalid cursor '{after}'"))


endpoints = dict(
    evaluate=dict(POST=do_evaluate),
    evaluation_events=dict(GET=do_evaluation_events),
)
