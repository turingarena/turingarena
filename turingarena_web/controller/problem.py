from flask import Blueprint, render_template, abort, request, send_file
from turingarena_web.model.contest import Contest

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

    if not Contest.exists_with_user_and_problem(current_user, problem):
        return abort(403)

    error = None
    if request.method == "POST":
        try:
            return evaluate(current_user, problem)
        except RuntimeError as e:
            error = str(e)

    subs = []

    if current_user is not None:
        subs = Submission.from_user_and_problem(current_user, problem)

    return render_template("problem.html", error=error, problem=problem, user=current_user, submissions=subs)


@problem_bp.route("/files/<name>.zip")
def files(name):
    problem = Problem.from_name(name)
    return send_file(problem.files_zip)
