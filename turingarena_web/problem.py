import os

from commonmark import commonmark
from flask import Blueprint, render_template, abort, request, send_from_directory

from turingarena_web.database import database
from turingarena_web.evaluate import evaluate
from turingarena_web.user import get_current_user

problem_bp = Blueprint("problem", __name__)


@problem_bp.route("/<name>", methods=("GET", "POST"))
def problem_view(name):
    current_user = get_current_user()
    if request.method == "POST" and current_user is None:
        return abort(401)

    problem = database.get_problem_by_name(name)

    error = None
    if request.method == "POST":
        try:
            return evaluate(current_user, problem)
        except RuntimeError as e:
            error = str(e)

    statement_file = os.path.join(problem.path, ".generated", "statement.md")
    statement = ""
    if os.path.exists(statement_file):
        with open(statement_file) as f:
            statement = commonmark(f.read())

    if problem is None:
        return abort(404)

    subs = []

    if current_user is not None:
        subs = database.get_submissions_by_user_and_problem(user_id=current_user.id, problem_id=problem.id)

    return render_template("problem.html", error=error, name=name, title=problem.title, statement=statement, user=current_user, submissions=subs)


@problem_bp.route("/files/<name>.zip")
def files(name):
    problem = database.get_problem_by_name(name)
    return send_from_directory(directory=problem.path, filename=f"{name}.zip")
