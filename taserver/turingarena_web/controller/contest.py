from flask import Blueprint, abort, render_template, redirect, url_for, request, send_file
from turingarena_web.controller.session import get_current_user
from turingarena_web.model.contest import Contest
from turingarena_web.controller import session
from turingarena_web.model.evaluate import evaluate
from turingarena_web.model.problem import Problem
from turingarena_web.model.submission import Submission


contest_bp = Blueprint("contest", __name__)


@contest_bp.route("/<contest_name>")
def contest_view(contest_name):
    contest = Contest.from_name(contest_name)

    if contest is None:
        return abort(404)

    user = session.get_current_user()

    if not contest.public and not contest.contains_user(user):
        return abort(403)

    return render_template("contest.html", contest=contest, user=user)


@contest_bp.route("/<contest_name>/subscribe")
def subscribe(contest_name):
    contest = Contest.from_name(contest_name)
    user = session.get_current_user()

    if contest is None:
        return abort(404)

    if user is None or not contest.public:
        return abort(403)

    contest.add_user(user)

    return redirect(url_for("contest.contest_view", contest_name=contest_name))


@contest_bp.route("/<contest_name>/<name>", methods=("GET", "POST"))
def problem_view(contest_name, name):
    contest = Contest.from_name(contest_name)
    if contest is None:
        return abort(404)

    current_user = get_current_user()
    if contest is None or not contest.contains_user(current_user):
        return abort(403)

    if request.method == "POST" and current_user is None:
        return abort(401)

    problem = Problem.from_name(name)
    if problem is None:
        return abort(404)

    error = None
    if request.method == "POST":
        try:
            return evaluate(current_user, problem, contest)
        except RuntimeError as e:
            error = str(e)

    subs = list(Submission.from_user_and_problem_and_contest(current_user, problem, contest))

    correct_goals = {
        sub.id: sum(val for val in sub.goals.values() if val is not None)
        for sub in subs
    }

    return render_template("problem.html", correct_goals=correct_goals, error=error, problem=problem, contest=contest, user=current_user, submissions=subs)


@contest_bp.route("/<contest_name>/<name>.zip")
def files(contest_name, name):
    problem = Problem.from_name(name)
    contest = Contest.from_name(contest_name)
    if problem is None or contest is None:
        return abort(404)
    return send_file(problem.zip_path(contest))
