from flask import Blueprint, abort
from turingarena_web.model.contest import Contest
from turingarena_web.controller.common import render_template_ex
from turingarena_web.controller import session

contest_bp = Blueprint("contest", __name__)


@contest_bp.route("/")
@contest_bp.route("/<string:contest_name>")
def contest(contest_name=None):
    if contest_name is None:
        contest = session.get_current_contest()
    else:
        contest = Contest.from_name(contest_name)

    if contest is None:
        return abort(404)

    user = session.get_current_user()

    if not contest.public and not contest.contains_user(user):
        return abort(403)

    session.set_current_contest(contest)
    return render_template_ex("contest.html", contest=contest)
