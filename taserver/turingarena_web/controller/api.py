from flask import Blueprint, request, jsonify
from turingarena_web.model.contest import Contest
from turingarena_web.model.submission import Submission, StoredEvaluationEvent
from turingarena_web.model.user import User
from turingarena_web.controller.session import get_current_user, set_current_user

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

    user = get_current_user()
    if user is None:
        return error(401, "authentication required")

    submission = Submission.from_id(submission_id)

    if submission is None:
        return error(400, "you provided an invalid submission id")

    if submission.user != user:
        return error(403, "you are trying to access a submission that is not yours")

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
    if args is None:
        return error(400, "missing request JSON arguments")

    user = get_current_user()
    if user is None:
        return error(401, "authentication required")

    if "name" not in args:
        return error(400, "missing required parameter name")

    contest = Contest.contest(args["name"])

    if contest is None:
        return error(404, f"contest {args['name']} not found")

    if contest not in user.contests:
        return error(403, f"you have not the permission to view this contest")

    return jsonify(contest=contest.as_json_data())


@api_bp.route("/problem", methods=("POST",))
def problem_api():
    args = request.json
    if args is None:
        return error(400, "missing request JSON arguments")

    user = get_current_user()
    if user is None:
        return error(401, "authentication required")

    if "name" not in args:
        return error(400, "missing required parameter name")
    if "contest" not in args:
        return error(400, "missing required parameter contest")

    contest = Contest.contest(args["contest"])
    if contest is None:
        return error(404, f"contest {args['contest']} not found")

    if contest not in user.contests:
        return error(403, f"you have not the permission to view this contest")

    problem = contest.problem(args["name"])
    if problem is None:
        return error(404, f"problem {args['name']} not found in contest {contest.name}")

    return jsonify(problem=problem.as_json_data())


@api_bp.route("/user", methods=("POST",))
def user_api():
    args = request.json
    if args is None:
        return error(400, "missing request JSON arguments")

    if "username" not in args:
        return error(400, "missing required argument username")

    current_user = get_current_user()
    if current_user is None:
        return error(401, "authentication required")

    user = User.from_username(args["username"])
    if user is None:
        return error(404, f"user {args['username']} does not exist")

    if current_user != user:
        return error(403, f"you are trying to access information of another user")

    return jsonify(user=user.as_json_data())


@api_bp.route("/auth", methods=("POST",))
def auth_api():
    args = request.json
    if args is None:
        return error(400, "missing request JSON arguments")

    if "username" not in args:
        return error(400, "missing required parameter username")
    if "password" not in args:
        return error(400, "missing required parameter password")

    user = User.from_username(args["username"])
    if user is None or not user.check_password(args["password"]):
        return error(401, "wrong username or password")

    set_current_user(user)
    return jsonify(status="OK")
