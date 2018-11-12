from flask import Blueprint, abort
from turingarena_web.contest import Contest
from turingarena_web.views.common import render_template_ex
from turingarena_web.views.user import get_current_user

contest_bp = Blueprint("contest", __name__)


@contest_bp.route("/<string:name>")
def contest(name):
    contest = Contest.from_name(name)

    if contest is None:
        return abort(404)

    user = get_current_user()

    if not contest.contains_user(user):
        return abort(403)

    return render_template_ex("contest.html", contest=contest)
