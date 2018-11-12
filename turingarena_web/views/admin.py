from flask import Blueprint, request, render_template, abort, redirect, url_for
from turingarena_web.problem import install_problem
from turingarena_web.views.common import render_template_ex, is_admin

from turingarena_web.database import database
from turingarena_web.views.user import get_current_user

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

        install_problem(url)
        return redirect(url_for("admin.problems"))
    return render_template_ex("admin/problems.html", problems=database.get_all_problems())


@admin_bp.route("/delete_problem/<int:problem_id>")
def problem_delete(problem_id):
    if not is_admin():
        return abort(403)
    database.delete_problem(problem_id)
    return redirect(url_for("admin.problems"))


@admin_bp.route("/users")
def users():
    return render_template_ex("admin/users.html", user=get_current_user())


