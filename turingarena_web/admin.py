import logging
import os
import subprocess

from flask import Blueprint, current_app, request, render_template, abort, redirect, url_for
from turingarena.file.generated import PackGeneratedDirectory

from turingarena_web.database import ProblemDatabase, UserPrivilege
from turingarena_web.user import get_current_user

admin_bp = Blueprint("admin", __name__)

problem_db = ProblemDatabase()

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
    title = f"TuringArena problem {name}"

    install_problem(name, url, title)
    return redirect(url_for("problem.problem_view", name=name))


@admin_bp.route("/users")
def users():
    return render_template("admin/users.html")

