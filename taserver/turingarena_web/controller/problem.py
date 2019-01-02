from flask import Blueprint, render_template, abort, request, send_file

from turingarena_web.controller import session

from turingarena_web.model.evaluate import evaluate
from turingarena_web.model.problem import Problem
from turingarena_web.model.submission import Submission
from turingarena_web.controller.session import get_current_user

problem_bp = Blueprint("problem", __name__)


@problem_bp.route("/<name>", methods=("GET", "POST"))
def problem_view(name):
    current_user = get_current_user()
    if request.method == "POST" and current_user is None:
        return abort(401)

    problem = Problem.from_name(name)
    if problem is None:
        return abort(404)

    contest = session.get_current_contest()
    if contest is None or not contest.contains_user(current_user):
        return abort(403)

    error = None
    if request.method == "POST":
        try:
            return evaluate(current_user, problem, contest)
        except RuntimeError as e:
            error = str(e)

    subs = []

    if current_user is not None:
        subs = Submission.from_user_and_problem_and_contest(current_user, problem, contest)

    return render_template("problem.html", error=error, problem=problem, contest=contest, user=current_user, submissions=subs)


@problem_bp.route("/files/<name>.zip")
def files(name):
    problem = Problem.from_name(name)
    contest = session.get_current_contest()
    if problem is None or contest is None:
        return abort(404)
    return send_file(problem.zip_path(contest))
