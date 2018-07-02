import base64
import json
import logging
import re
import secrets
import time
from collections import namedtuple
from http import HTTPStatus

import boto3

from turingarena_impl.api.common import ProxyError

SUBMISSION_FIELDS_RE = re.compile(r"submission\[([a-z]+(_[a-z])*)\]")

SubmissionFile = namedtuple("SubmissionFile", ["filename", "content"])


def get_submission_files(params, used_params):
    for p in params:
        match = SUBMISSION_FIELDS_RE.fullmatch(p)
        if not match:
            continue

        name = match.group(1)
        used_params.add(p)

        filename = params[p].filename
        content = params[p].value
        if not isinstance(content, bytes):
            raise ProxyError(HTTPStatus.BAD_REQUEST, dict(message=f"Field '{p}' is not a file"))
        yield name, SubmissionFile(filename=filename, content=content)


def save_submission(id, files):
    submission_json = {
        "files": {
            name: {
                "filename": file_data.filename,
                "content": base64.b64encode(file_data.content).decode()
            }
            for name, file_data in files.items()
        }
    }

    client = boto3.client("dynamodb")

    client.put_item(
        TableName='SubmissionsTable',
        Item={
            'id': {
                'S': id,
            },
            'expires': {
                'N': str(int(time.time() + 10 * 60)),
            },
            'data': {
                'S': json.dumps(submission_json),
            }
        },
    )


def do_evaluate(params):
    used_params = set()

    submission = dict(get_submission_files(params, used_params))

    unused_params = set(params) - used_params
    if unused_params:
        unused_params_list = ", ".join(unused_params)
        message = f"Unexpected params: {unused_params_list}"
        raise ProxyError(HTTPStatus.BAD_REQUEST, dict(message=message))

    submission_id = secrets.token_hex(16)

    save_submission(submission_id, submission)

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
