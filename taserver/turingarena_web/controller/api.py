from flask import Blueprint, request, jsonify
from turingarena_web.model.contest import Contest
from turingarena_web.model.evaluate import evaluate
from turingarena_web.model.submission import Submission
from turingarena_web.model.user import User
from turingarena_web.controller.session import get_current_user, set_current_user

api_bp = Blueprint("api", __name__)


class ApiError(Exception):
    def __init__(self, status_code, message):
        self.message = message
        self.status_code = status_code


def error(status_code, message):
    response = jsonify(
        status=status_code,
        message=message,
    )
    response.status_code = status_code
    return response


@api_bp.errorhandler(ApiError)
def handle_api_error(e):
    return error(e.status_code, e.message)


class Args:
    def __init__(self):
        self.args = request.json
        if self.args is None:
            raise ApiError(400, "invalid request JSON args")

    def __getattr__(self, item):
        if item not in self.args:
            raise ApiError(400, f"missing parameter {item}")
        return self.args[item]

    def __getitem__(self, item):
        return self.args[item]

    def __contains__(self, item):
        return item in self.args


def require_auth():
    user = get_current_user()
    if user is None:
        raise ApiError(401, "authentication required")
    return user


@api_bp.route("/events", methods=("POST",))
def evaluation_event():
    args = Args()
    user = require_auth()
    submission = Submission.from_id(args.id)

    if submission is None:
        raise ApiError(400, "you provided an invalid submission id")

    if submission.user != user:
        raise ApiError(403, "you are trying to access a submission that is not yours")

    after = 0
    if "after" in args:
        after = args["after"]
        if not isinstance(after, int):
            raise ApiError(400, "the after parameter must be an integer")

    events = [
        event.as_json_data()
        for event in submission.events(after)
    ]

    return jsonify(events=events)


@api_bp.route("/submission", methods=("POST",))
def submission_api():
    args = Args()

    user = require_auth()

    submission = Submission.from_id(args.id)
    if submission is None:
        raise ApiError(404, f"no submission with id {args.id}")

    if submission.user != user:
        raise ApiError(403, f"you are trying to get information on a submission that is not yours")

    return jsonify(submission.as_json_data())


@api_bp.route("/contest", methods=("POST",))
def contest_api():
    args = Args()
    user = require_auth()
    contest = Contest.contest(args.name)

    if contest is None:
        raise ApiError(404, f"contest {args.name} not found")

    if contest not in user.contests:
        raise ApiError(403, f"you have not the permission to view this contest")

    return jsonify(contest.as_json_data())


@api_bp.route("/problem", methods=("POST",))
def problem_api():
    args = Args()
    user = require_auth()
    contest = Contest.contest(args.contest)
    if contest is None:
        raise ApiError(404, f"contest {args['contest']} not found")

    if contest not in user.contests:
        raise ApiError(403, f"you have not the permission to view this contest")

    problem = contest.problem(args.name)
    if problem is None:
        raise ApiError(404, f"problem {args.name} not found in contest {contest.name}")

    return jsonify(problem.as_json_data())


@api_bp.route("/evaluate", methods=("POST",))
def evaluate_api():
    args = Args()
    user = require_auth()
    contest = Contest.contest(args.contest)
    if contest is None:
        raise ApiError(404, f"contest {args.contest} not found")

    if contest not in user.contests:
        raise ApiError(403, "you have not the permission to submit in this contest")

    problem = contest.problem(args.problem)
    if problem is None:
        raise ApiError(404, f"problem {args.name} not found in contest {contest.name}")

    if not isinstance(args.files, dict):
        raise ApiError(400, "files parameter must be a dict")

    if "source" not in args.files:
        raise ApiError(400, "missing source file")

    source = args.files["source"]
    if not isinstance(source, dict):
        raise ApiError(400, "source parameter must be a dict")

    if "filename" not in source:
        raise ApiError(400, "missing filename for source file")
    if "content" not in source:
        raise ApiError(400, "missing content for source file")

    submission = evaluate(user, problem, contest, source)

    return jsonify(submission.as_json_data())


@api_bp.route("/user", methods=("POST",))
def user_api():
    args = Args()
    current_user = require_auth()
    user = User.from_username(args.username)
    if user is None:
        raise ApiError(404, f"user {args.username} does not exist")

    if current_user != user:
        raise ApiError(403, f"you are trying to access information of another user")

    return jsonify(user.as_json_data())


@api_bp.route("/auth", methods=("POST",))
def auth_api():
    args = Args()

    user = User.from_username(args.username)
    if user is None or not user.check_password(args.password):
        raise ApiError(401, "wrong username or password")

    set_current_user(user)
    return jsonify(status="OK")
