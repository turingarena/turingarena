from flask import Blueprint, request, jsonify
from datetime import datetime

from turingarena_web.model.user import User
from turingarena_web.model.contest import Contest
from turingarena_web.model.submission import Submission
from turingarena_web.controller.user import get_current_user, set_current_user


api = Blueprint("api", __name__)


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


@api.errorhandler(ApiError)
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


def require_auth(contest):
    user = get_current_user(contest)
    if user is None:
        raise ApiError(401, "authentication required")
    return user


@api.route("/events", methods=("POST",))
def evaluation_event():
    args = Args()
    user = require_auth(args.contest)
    contest = Contest(args.contest)
    problem = contest.problem(args.problem)
    time = datetime.fromtimestamp(args.timestamp)
    submission = Submission(contest, problem, user, time)

    if not submission.exists:
        raise ApiError(404, "the specified submission does not exist")

    after = 0
    if "after" in args:
        after = args["after"]
        if not isinstance(after, int):
            raise ApiError(400, "the after parameter must be an integer")

    events = [
        event
        for event in submission.events(after)
    ]

    return jsonify(events=events)


@api.route("/submission", methods=("POST",))
def submission_api():
    args = Args()
    user = require_auth(args.contest)
    contest = Contest(args.contest)
    problem = contest.problem(args.problem)
    time = args.timestamp
    submission = Submission(contest, problem, user, time)
    if not submission.exists:
        return error(404, "the specified submission doesn't exists")

    return jsonify(submission.as_json_data())


@api.route("/contest", methods=("POST",))
def contest_api():
    args = Args()
    user = require_auth(args.contest)
    contest = Contest.contest(args.name)

    if contest is None:
        raise ApiError(404, f"contest {args.name} not found")

    return jsonify(contest.as_json_data())


@api.route("/problem", methods=("POST",))
def problem_api():
    args = Args()
    user = require_auth(args.contest)
    contest = Contest.contest(args.contest)
    if contest is None:
        raise ApiError(404, f"contest {args['contest']} not found")

    problem = contest.problem(args.name)
    if problem is None:
        raise ApiError(404, f"problem {args.name} not found in contest {contest.name}")

    return jsonify(problem.as_json_data())


@api.route("/evaluate", methods=("POST",))
def evaluate_api():
    args = Args()
    user = require_auth(args.contest)
    contest = Contest.contest(args.contest)
    if contest is None:
        raise ApiError(404, f"contest {args.contest} not found")

    problem = contest.problem(args.problem)
    if problem is None:
        raise ApiError(404, f"problem {args.name} not found in contest {contest.name}")

    if not isinstance(args.files, dict):
        raise ApiError(400, "files parameter must be a dict")

    files = {
        name: dict(
            filename=file["filename"],
            content=file["content"],
        )
        for name, file in args.files.items()
    }

    submission = Submission.new(user, problem, contest, files)

    return jsonify(submission.as_json_data())


@api.route("/auth", methods=("POST",))
def auth_api():
    args = Args()
    contest = Contest.contest(args.contest)
    if contest is None:
        raise ApiError(400, f"Invalid contest {args.contest}")

    if args.username is None:
        set_current_user(contest, None)
    else:
        user = User.from_username(contest, args.username)
        if user is None or not user.check_password(args.password):
            raise ApiError(401, "wrong username or password")

        set_current_user(args.contest, user)
    return jsonify(status="OK")
