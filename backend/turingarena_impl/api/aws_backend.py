import os
import pickle
import secrets
from http import HTTPStatus
from urllib.request import urlopen

from turingarena_common.commands import WorkingDirectory, Pack, GitRepository, EvaluateRequest
from turingarena_common.submission import SubmissionFile

from turingarena_impl.api.common import ProxyError
from turingarena_impl.api.dynamodb_events import load_event_page
from turingarena_impl.api.dynamodb_files import fetch_file
from turingarena_impl.api.request import CloudEvaluateRequest, CloudGenerateFileRequest


def get_children_field(base, params):
    for p in params:
        if not p.startswith(base + "["):
            continue
        name = p[len(base) + 1:]
        name = name[:name.index("]")]
        yield name


def get_submission_files(params, used_params):
    for n in get_children_field("submission", params):
        p_name = f"submission[{n}]"
        used_params.add(p_name)

        p = params[p_name]
        filename = p.filename
        content = p.value
        if not isinstance(content, bytes):
            raise ProxyError(HTTPStatus.BAD_REQUEST, dict(message=f"Field '{p_name}' is not a file"))
        yield n, SubmissionFile(filename=filename, content=content)


def do_evaluate(params):
    used_params = set()

    evaluation_id = secrets.token_hex(16)
    submission = dict(get_submission_files(params, used_params))

    working_directory = get_working_directory(params)

    request = CloudEvaluateRequest(
        evaluation_id=evaluation_id,
        evaluate_request=EvaluateRequest(
            submission=submission,
            working_directory=working_directory,
            seed=None,
        )
    )

    # check_no_unused_params(params, used_params)

    send_request_to_hypersh(request)

    return dict(
        id=evaluation_id,
    )


def send_request_to_hypersh(request):
    region = os.environ["HYPERSH_REGION"]
    func_name = os.environ["HYPERSH_FUNC_NAME"]
    func_id = os.environ["HYPERSH_FUNC_ID"]

    data = pickle.dumps(request)
    url = f"https://{region}.hyperfunc.io/call/{func_name}/{func_id}"
    with urlopen(url, data=data) as f:
        f.read()


def get_working_directory(params):
    current_directory = params.getfirst(f"directory")
    if current_directory is None:
        current_directory = "."

    working_directory = WorkingDirectory(
        pack=Pack(
            oid=params.getfirst("oid"),
            repository=GitRepository(
                url=params.getfirst(f"repository[url]"),
                branch=params.getfirst(f"repository[branch]"),
                depth=params.getfirst(f"repository[depth]"),
            )
        ),
        current_directory=current_directory,
    )

    return working_directory


def check_no_unused_params(params, used_params):
    unused_params = set(params) - used_params
    if unused_params:
        unused_params_list = ", ".join(unused_params)
        message = f"Unexpected params: {unused_params_list}"
        raise ProxyError(HTTPStatus.BAD_REQUEST, dict(message=message))


def do_evaluation_events(params):
    try:
        evaluation_id = params["evaluation"]
    except KeyError:
        raise ProxyError(HTTPStatus.BAD_REQUEST, dict(message=f"Missing parameter 'evaluation'"))

    # FIXME: use some opaque string for cursors

    after = params.get("after", None)
    if after is not None:
        after = int(after)

    return load_event_page(evaluation_id, after)


def do_generate_file(params):
    working_directory = get_working_directory(params)

    file_id = secrets.token_hex(16)

    request = CloudGenerateFileRequest(
        file_id=file_id,
        working_directory=working_directory,
    )

    send_request_to_hypersh(request)

    return dict(
        id=file_id,
    )


def do_get_file(params):
    try:
        file_id = params.getfirst("file")
    except KeyError:
        raise ProxyError(HTTPStatus.BAD_REQUEST, dict(message=f"Missing parameter 'file'"))

    return fetch_file(file_id)


endpoints = dict(
    evaluate=dict(POST=do_evaluate),
    evaluation_events=dict(GET=do_evaluation_events),
    generate_file=dict(POST=do_generate_file),
    get_file=dict(POST=do_get_file),
)
