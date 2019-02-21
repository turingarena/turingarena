from flask import Blueprint, request, jsonify
from turingarena_web.model.submission import Submission, EvaluationEvent

api_bp = Blueprint("api", __name__)


def error(status_code, message):
    response = jsonify(
        status=status_code,
        message=message,
    )
    response.status_code = status_code
    return response


@api_bp.route("/evaluation_event")
def evaluation_event():
    submission_id = request.args.get("id", None)

    if submission_id is None:
        return error(400, "you must specify a submission id")

    submission = Submission.from_id(submission_id)

    if submission is None:
        return error(400, "you provided an invalid submission id")

    try:
        after = int(request.args.get("after", 0))
    except ValueError:
        return error(400, "the after parameter must be an integer")

    events = [
        {"serial": event.serial, "type": event.type.value, "payload": event.data}
        for event in EvaluationEvent.from_submission(submission, after=after)
    ]

    return jsonify(events)
