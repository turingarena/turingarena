import os

from flask import Blueprint, render_template, send_from_directory, current_app

from turingarena_web.admin import problem_db

root = Blueprint('root', __name__)


@root.route("/")
def problems_view():
    problems = problem_db.get_all()
    return render_template("problems.html", problems=problems)


@root.route('/favicon.ico')
def favicon():
    # TODO: not all browsers supports SVG favicon. Check if browser is supported and if not serve a standard PNG image
    return send_from_directory(
        directory=os.path.join(current_app.root_path, 'static/img'),
        filename='turingarena_logo.svg'
    )
