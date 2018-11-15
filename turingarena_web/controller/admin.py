from flask import Blueprint, request, render_template, abort, redirect, url_for
from turingarena_web.model.problem import Problem
from turingarena_web.controller.common import render_template_ex, is_admin

from turingarena_web.controller.session import get_current_user

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/")
def home():
    return render_template("admin/admin.html", user=get_current_user())


@admin_bp.route("/problems", methods=("GET", "POST", "DELETE"))
def problems():
    if not is_admin():
        return abort(403)
    if request.method == "POST":
        url = request.form["url"]
        if "://" not in url:
            url = "https://github.com/" + url

        Problem.install(url)
        return redirect(url_for("admin.problems"))
    return render_template_ex("admin/home.html", problems=Problem.problems())


@admin_bp.route("/delete_problem/<int:problem_name>")
def problem_delete(problem_name):
    if not is_admin():
        return abort(403)
    problem = Problem.from_name(problem_name)
    problem.delete()
    return redirect(url_for("admin.problems"))


@admin_bp.route("/users")
def users():
    return render_template_ex("admin/users.html", user=get_current_user())


