import os
import logging
import subprocess

from commonmark import commonmark
from flask import Blueprint, render_template, abort, redirect, url_for, request, current_app, send_from_directory
from turingarena.file.generated import PackGeneratedDirectory

from turingarena_web.database import ProblemDatabase

problem_bp = Blueprint("problem", __name__)
problem_db = ProblemDatabase()


def git_clone(url, directory):
    logging.debug(f"git clone {url} -> {directory}")
    subprocess.call(["git", "clone", url, directory])


def install_problem(name, problem_url, title=None):
    if title is None:
        title = name
    problem_dir = os.path.join(current_app.config["PROBLEMS_DIR"], name)

    if os.path.exists(problem_dir):
        subprocess.call(["rm", "-rf", problem_dir])

    git_clone(problem_url, problem_dir)
    files_dir = os.path.join(problem_dir, ".generated")
    os.mkdir(files_dir)

    pd = PackGeneratedDirectory(problem_dir)

    for filename, generator in pd.targets:
        os.makedirs(os.path.split(filename)[0], exist_ok=True)
        with open(os.path.join(files_dir, filename), "w") as file:
            generator(file)

    files_zip = os.path.join(problem_dir, f"{name}.zip")
    os.chdir(files_dir)
    subprocess.call(["zip", "-r", files_zip, "."])

    problem_db.insert(name=name, title=title, location=problem_url)


@problem_bp.route("/install", methods=("GET", "POST"))
def install():
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
    problems_dir = current_app.config["PROBLEMS_DIR"]

    if request.method == "POST":
        # TODO: generate submission
        submission_id = None
        return redirect(url_for("submission.submission_view", id=submission_id))

    statement_file = os.path.join(problems_dir, name, ".generated", "statement.md")
    statement = ""
    if os.path.exists(statement_file):
        with open(statement_file) as f:
            statement = commonmark(f.read())

    problem = problem_db.get_by_name(name)
    if problem is None:
        return abort(404)
    return render_template("problem.html", name=name, title=problem.title, statement=statement)


@problem_bp.route("/files/<name>.zip")
def files(name):
    problems_dir = current_app.config["PROBLEMS_DIR"]
    return send_from_directory(directory=os.path.join(problems_dir, name), filename=f"{name}.zip")

