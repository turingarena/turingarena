import logging
import os
import subprocess
import threading
from datetime import datetime

from commonmark import commonmark
from flask import Blueprint, render_template, abort, redirect, url_for, request, current_app, send_from_directory
from turingarena.file.generated import PackGeneratedDirectory

from turingarena_web.database import ProblemDatabase, UserDatabase, SubmissionDatabase, UserPrivilege
from turingarena_web.evaluate import evaluate
from turingarena_web.submission import submitted_file_path
from turingarena_web.user import get_current_user

problem_bp = Blueprint("problem", __name__)
problem_db = ProblemDatabase()
submission_db = SubmissionDatabase()
user_db = UserDatabase()


def git_clone(url, directory):
    logging.debug(f"git clone {url} -> {directory}")
    subprocess.call(["git", "clone", url, directory])


def problem_dir(name):
    return current_app.config["PROBLEM_DIR_PATH"].format(name=name)


def install_problem(name, problem_url, title=None):
    if title is None:
        title = name

    if os.path.exists(problem_dir(name)):
        subprocess.call(["rm", "-rf", problem_dir(name)])

    git_clone(problem_url, problem_dir(name))
    files_dir = os.path.join(problem_dir(name), ".generated")
    os.mkdir(files_dir)

    pd = PackGeneratedDirectory(problem_dir(name))

    for filename, generator in pd.targets:
        os.makedirs(os.path.split(filename)[0], exist_ok=True)
        with open(os.path.join(files_dir, filename), "w") as file:
            generator(file)

    files_zip = os.path.join(problem_dir(name), f"{name}.zip")
    os.chdir(files_dir)
    subprocess.call(["zip", "-r", files_zip, "."])

    problem_db.insert(name=name, title=title, location=problem_url, path=problem_dir(name))


@problem_bp.route("/install", methods=("GET", "POST"))
def install():
    if get_current_user() is None or get_current_user().privilege != UserPrivilege.ADMIN.value:
        return abort(401)
    if request.method == "GET":
        return render_template("problem_install.html")
    url = request.form["url"]
    if "://" not in url:
        url = "https://github.com/" + url
    name = os.path.basename(url)
    title = f"TuringArena problem {name}"

    install_problem(name, url, title)
    return redirect(url_for("problem.problem_view", name=name))


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
