from flask import Blueprint, request, jsonify
from turingarena_web.model.contest import Contest
from turingarena_web.model.submission import Submission, StoredEvaluationEvent
from turingarena_web.model.user import User

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
        event.event.as_json_data()
        for event in StoredEvaluationEvent.from_submission(submission, after=after)
    ]

    return jsonify(events=events)


@api_bp.route("/contest", methods=("POST",))
def contest_api():
    args = request.json

    if "name" not in args:
        return error(400, "missing required parameter name")

    contest = Contest.contest(args["name"])

    if contest is None:
        return error(404, f"contest {args['name']} not found")

    return jsonify(contest=contest.as_json_data())


@api_bp.route("/problem", methods=("POST",))
def problem_api():
    args = request.json

    if "name" not in args:
        return error(400, "missing required parameter name")
    if "contest" not in args:
        return error(400, "missing required parameter contest")

    contest = Contest.contest(args["contest"])
    if contest is None:
        return error(404, f"contest {args['contest']} not found")

    problem = contest.problem(args["name"])
    if problem is None:
        return error(404, f"problem {args['name']} not found in contest {contest.name}")

    return jsonify(problem=problem.as_json_data())


@api_bp.route("/user", methods=("POST",))
def user_api():
    args = request.json

    if "username" not in args:
        return error(400, "missing required argument username")

    user = User.from_username(args["username"])
    if user is None:
        return error(404, f"user {args['username']} does not exist")

    return jsonify(user=user.as_json_data())

