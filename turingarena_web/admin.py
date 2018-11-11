import logging
import os
import subprocess

from flask import Blueprint, current_app, request, render_template, abort, redirect, url_for
from turingarena.evallib.metadata import load_metadata
from turingarena.file.generated import PackGeneratedDirectory

from turingarena_web.database import database, UserPrivilege
from turingarena_web.user import get_current_user

admin_bp = Blueprint("admin", __name__)


def clone_from_git(url, directory):
    os.mkdir(directory)
    logging.debug(f"git clone {url} -> {directory}")
    subprocess.call(["git", "clone", url, directory])


def generate_problem_files(problem_dir, name):
    files_dir = os.path.join(problem_dir, ".generated")
    os.mkdir(files_dir)

    pd = PackGeneratedDirectory(problem_dir, allowed_languages=current_app.config.get("ALLOWED_LANGUAGES", None))

    for path, generator in pd.targets:
        directory = os.path.join(files_dir, os.path.split(path)[0])
        filename = os.path.split(path)[1]
        os.makedirs(directory, exist_ok=True)
        with open(os.path.join(directory, filename), "w") as file:
            generator(file)

    files_zip = os.path.join(problem_dir, f"{name}.zip")
    os.chdir(files_dir)
    subprocess.call(["zip", "-r", files_zip, "."])


def install_problem(name, problem_url, title=None):
    if title is None:
        title = name

    problem_dir = current_app.config["PROBLEM_DIR_PATH"].format(name=name)

    if os.path.exists(problem_dir):
        subprocess.call(["rm", "-rf", problem_dir])

    clone_from_git(problem_url, problem_dir)
    generate_problem_files(problem_dir, name)

    metadata = load_metadata(problem_dir)
    scoring_metadata = metadata.get("scoring", {})
    goals = scoring_metadata.get("goals", [])

    database.insert_problem(name=name, title=title, location=problem_url, path=problem_dir, goals=goals)


@admin_bp.route("/")
def home():
    return redirect(url_for("admin.installx"))


@admin_bp.route("/problems", methods=("GET", "POST"))
def install():
    if request.method == "GET":
        return render_template("admin/problem_install.html")
    if get_current_user() is None or get_current_user().privilege != UserPrivilege.ADMIN.value:
        return abort(401)
    if request.method == "GET":
        return render_template("admin/problem_install.html")
    url = request.form["url"]
    if "://" not in url:
        url = "https://github.com/" + url
    name = os.path.basename(url)

    install_problem(name, url)
    return redirect(url_for("problem.problem_view", name=name))


@admin_bp.route("/users")
def users():
    return render_template("admin/users.html")

