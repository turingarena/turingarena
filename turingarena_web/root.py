import os

from flask import Blueprint, render_template, send_from_directory, current_app, redirect, url_for

from turingarena_web.admin import database
from turingarena_web.user import get_current_user

root_bp = Blueprint('root', __name__)


@root_bp.route("/")
def home():
    return redirect(url_for("root.problems_view"))


@root_bp.route("/problems")
def problems_view():
    problems = database.get_all_problems()
    return render_template("problems.html", problems=problems, user=get_current_user())


@root_bp.route('/favicon.ico')
def favicon():
    # TODO: not all browsers supports SVG favicon. Check if browser is supported and if not serve a standard PNG image
    return send_from_directory(
        directory=os.path.join(current_app.root_path, 'static/img'),
        filename='turingarena_logo.svg'
    )
