import os
import threading
from datetime import datetime

from commonmark import commonmark
from flask import Blueprint, render_template, abort, redirect, url_for, request, current_app, send_from_directory

from turingarena_web.database import ProblemDatabase, UserDatabase, SubmissionDatabase, UserPrivilege
from turingarena_web.evaluate import evaluate
from turingarena_web.submission import submitted_file_path
from turingarena_web.user import get_current_user

problem_bp = Blueprint("problem", __name__)
problem_db = ProblemDatabase()
submission_db = SubmissionDatabase()
user_db = UserDatabase()


@problem_bp.route("/")
def problems_view():
    problems = problem_db.get_all()
    return render_template("problems.html", problems=problems)


@problem_bp.route("/<name>", methods=("GET", "POST"))
def problem_view(name):
    current_user = get_current_user()
    if request.method == "POST" and current_user is None:
        return abort(401)

    problem = problem_db.get_by_name(name)

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

        submission_id = submission_db.insert_submission(
            user_id=current_user.id,
            problem_id=problem.id,
            filename=submitted_file.filename,
            path=path,
        )
        submission = submission_db.get_by_id(submission_id)
        threading.Thread(target=evaluate, args=(problem, submission, current_app._get_current_object())).start()

        assert submission_id is not None
        return redirect(url_for("submission.submission_view", id=submission_id))

    statement_file = os.path.join(problem.path, ".generated", "statement.md")
    statement = ""
    if os.path.exists(statement_file):
        with open(statement_file) as f:
            statement = commonmark(f.read())

    if problem is None:
        return abort(404)
    return render_template("problem.html", name=name, title=problem.title, statement=statement, user=current_user)


@problem_bp.route("/files/<name>.zip")
def files(name):
    problem = problem_db.get_by_name(name)
    return send_from_directory(directory=problem.path, filename=f"{name}.zip")
