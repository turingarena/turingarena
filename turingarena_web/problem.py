import os
import threading
from datetime import datetime

from commonmark import commonmark
from flask import Blueprint, render_template, abort, redirect, url_for, request, current_app, send_from_directory

from turingarena_web.database import database
from turingarena_web.evaluate import evaluate
from turingarena_web.submission import submitted_file_path
from turingarena_web.user import get_current_user

problem_bp = Blueprint("problem", __name__)


@problem_bp.route("/<name>", methods=("GET", "POST"))
def problem_view(name):
    current_user = get_current_user()
    if request.method == "POST" and current_user is None:
        return abort(401)

    problem = database.get_problem_by_name(name)

    if request.method == "POST":
        timestamp = datetime.now()

        submitted_file = request.files["source"]
        path = submitted_file_path(
            problem_name=problem.name,
            username=current_user.username,
            timestamp=timestamp,
            filename=submitted_file.filename,
        )

        os.makedirs(os.path.split(path)[0], exist_ok=True)
        submitted_file.save(path)

        submission_id = database.insert_submission(
            user_id=current_user.id,
            problem_id=problem.id,
            filename=submitted_file.filename,
            path=path,
        )
        submission = database.get_submission_by_id(submission_id)
        threading.Thread(target=evaluate, args=(problem, submission, current_app._get_current_object())).start()

        assert submission_id is not None
        return redirect(url_for("submission.submission_view", submission_id=submission_id))

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

    return render_template("problem.html", name=name, title=problem.title, statement=statement, user=current_user, submissions=subs)


@problem_bp.route("/files/<name>.zip")
def files(name):
    problem = database.get_problem_by_name(name)
    return send_from_directory(directory=problem.path, filename=f"{name}.zip")
