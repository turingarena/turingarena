import logging
import re
import secrets
from http import HTTPStatus

from turingarena_impl.api.common import ProxyError

SUBMISSION_FIELDS_RE = re.compile(r"submission\[([a-z]+(_[a-z])*)\]")


def get_submission_files(params, used_params):
    for p in params:
        match = SUBMISSION_FIELDS_RE.fullmatch(p)
        if not match:
            continue

        name = match.group(1)
        used_params.add(p)

        source = params[p].value
        if not isinstance(source, bytes):
            raise ProxyError(HTTPStatus.BAD_REQUEST, dict(message=f"Field '{p}' is not a file"))
        yield name, source


def do_evaluate(params):
    used_params = set()

    submission = dict(get_submission_files(params, used_params))

    unused_params = set(params) - used_params
    if unused_params:
        unused_params_list = ", ".join(unused_params)
        message = f"Unexpected params: {unused_params_list}"
        raise ProxyError(HTTPStatus.BAD_REQUEST, dict(message=message))

    submission_id = secrets.token_hex(16)

    logging.info(f"submission fields: {list(submission.keys())}")

    return dict(
        id=submission_id,
    )


def do_evaluation_events(params):
    try:
        evaluation_id = params["evaluation"]
    except KeyError:
        raise ProxyError(HTTPStatus.BAD_REQUEST, dict(message=f"Missing parameter 'evaluation'"))

    after = params.get("after", None)
    if after:
        raise ProxyError(HTTPStatus.NOT_FOUND, dict(message=f"Invalid cursor '{after}'"))


endpoints = dict(
    evaluate=dict(POST=do_evaluate),
    evaluation_events=dict(GET=do_evaluation_events),
)
