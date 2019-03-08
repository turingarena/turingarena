from flask import Blueprint, abort, render_template, redirect, url_for, request, send_file

from turingarena.evaluation.submission import SubmissionFile

from turingarena_web.controller import session
from turingarena_web.model.contest import Contest
from turingarena_web.model.submission import Submission
from turingarena_web.controller.session import get_current_user


contest_bp = Blueprint("contest", __name__)


@contest_bp.route("/<contest_name>")
def contest_view(contest_name):
    contest = Contest.contest(contest_name)

    if contest is None:
        return abort(404)

    user = session.get_current_user()

    if user is None:
        return redirect("user.login")

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
    if current_user is None:
        return redirect("user.login")

    if contest not in current_user.contests:
        return abort(403)

    problem = contest.problem(name)
    if problem is None:
        return abort(404)

    error = None
    if request.method == "POST":
        try:
            files = {
                name: SubmissionFile(
                    filename=file.filename,
                    content=file.read().decode("utf-8"),
                )
                for name, file in request.files.items()
            }
            submission = Submission.new(current_user, problem, contest, files)
            return redirect(url_for("submission.submission_view",
                                    contest=contest.name,
                                    problem=problem.name,
                                    timestamp=submission.timestamp,
                                    ))
        except RuntimeError as e:
            error = str(e)

    subs = list(Submission.from_user_and_problem_and_contest(current_user, problem, contest))

    return render_template("problem.html", error=error, problem=problem, contest=contest, user=current_user,
                           submissions=subs)


@contest_bp.route("/<contest_name>/<name>.zip")
def files(contest_name, name):
    contest = Contest.contest(contest_name)
    problem = contest.problem(name)
    user = get_current_user()
    if user is None:
        return redirect("user.login")
    if problem is None or contest is None:
        return abort(404)
    if user not in contest.users():
        return abort(403)
    return send_file(problem.files_zip)
