from flask import Blueprint, abort, render_template, redirect, url_for, request, send_file
from turingarena_web.controller.session import get_current_user
from turingarena_web.model.contest import Contest
from turingarena_web.controller import session
from turingarena_web.model.evaluate import evaluate
from turingarena_web.model.submission import Submission


contest_bp = Blueprint("contest", __name__)


@contest_bp.route("/<contest_name>")
def contest_view(contest_name):
    contest = Contest.contest(contest_name)

    if contest is None:
        return abort(404)

    user = session.get_current_user()

    if user is None:
        return abort(401)

    if contest not in user.contests:
        if contest.public:
            user.add_to_contest(contest)
        else:
            return abort(403)

    return render_template("contest.html", contest=contest, user=user)


@contest_bp.route("/<contest_name>/<name>", methods=("GET", "POST"))
def problem_view(contest_name, name):
    contest = Contest.contest(contest_name)

    if contest is None:
        return abort(404)

    current_user = get_current_user()
    if current_user is None or contest not in current_user.contests:
        return abort(401)

    problem = contest.problem(name)
    if problem is None:
        return abort(404)

    error = None
    if request.method == "POST":
        try:
            file = request.files["source"]
            file = {
                "filename": file.filename,
                "content": file.read(),
            }
            submission = evaluate(current_user, problem, contest, file)
            return redirect(url_for("submission.submission_view", submission_id=submission.id))
        except RuntimeError as e:
            error = str(e)

    subs = list(Submission.from_user_and_problem_and_contest(current_user, problem, contest))

    return render_template("problem.html", error=error, problem=problem, contest=contest, user=current_user, submissions=subs)


@contest_bp.route("/<contest_name>/<name>.zip")
def files(contest_name, name):
    contest = Contest.contest(contest_name)
    problem = contest.problem(name)
    user = get_current_user()
    if user is None:
        return abort(401)
    if problem is None or contest is None:
        return abort(404)
    return send_file(problem.files_zip)
