import os
import pickle
import secrets
from http import HTTPStatus
from urllib.request import urlopen

from turingarena_common.commands import WorkingDirectory, Pack, GitRepository
from turingarena_common.submission import SubmissionFile
from turingarena_impl.api.common import ProxyError
from turingarena_impl.api.dynamodb_events import load_event_page
from turingarena_impl.api.dynamodb_submission import save_submission
from turingarena_impl.api.request import CloudEvaluateRequest


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

    submission = dict(get_submission_files(params, used_params))
    submission_id = secrets.token_hex(16)

    save_submission(submission_id, submission)

    current_directory = params.getfirst(f"directory")
    if current_directory is None:
        current_directory = "."

    working_directory = WorkingDirectory(
        pack=Pack(
            commit_oid=params.getfirst("commit_oid"),
            repository=GitRepository(
                url=params.getfirst(f"repository[url]"),
                branch=params.getfirst(f"repository[branch]"),
                depth=params.getfirst(f"repository[depth]"),
            )
        ),
        current_directory=current_directory,
    )

    request = CloudEvaluateRequest(
        submission_id=submission_id,
        evaluation_id=submission_id,
        evaluator=params["evaluator_cmd"].value,
        working_directory=working_directory,
    )

    # check_no_unused_params(params, used_params)

    region = os.environ["HYPERSH_REGION"]
    func_name = os.environ["HYPERSH_FUNC_NAME"]
    func_id = os.environ["HYPERSH_FUNC_ID"]

    data = pickle.dumps(request)
    url = f"https://{region}.hyperfunc.io/call/{func_name}/{func_id}"
    with urlopen(url, data=data) as f:
        f.read()

    return dict(
        id=submission_id,
    )


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


endpoints = dict(
    evaluate=dict(POST=do_evaluate),
    evaluation_events=dict(GET=do_evaluation_events),
)
