import os

from datetime import datetime
from flask import Blueprint, abort, render_template, redirect, url_for, send_file, current_app

from turingarena_web.model.contest import Contest
from turingarena_web.model.submission import Submission
from turingarena_web.controller.user import get_current_user


root = Blueprint("main", __name__, static_url_path="")


@root.route("/")
def home():
    contests = Contest.contests()

    return render_template("home.html", contests=sorted(contests, key=lambda x: x.title))


@root.route("/favicon.ico")
def favicon():
    return current_app.send_static_file("icon/favicon.ico")


@root.route("/<contest_name>")
def contest_view(contest_name):
    contest = Contest.contest(contest_name)

    user = get_current_user(contest_name)
    if user is None:
        return redirect(url_for("main.login", contest_name=contest_name))

    if contest is None:
        return abort(404)

    return render_template("contest.html", contest=contest, user=user)


@root.route("/<contest_name>/login")
def login(contest_name):
    contest = Contest.contest(contest_name)
    if contest is None:
        return abort(404)
    return render_template("login.html", contest=contest)


@root.route("/<contest_name>/<name>")
def problem_view(contest_name, name):
    contest = Contest.contest(contest_name)

    if contest is None:
        return abort(404)

    current_user = get_current_user(contest_name)
    if current_user is None:
        return redirect("user.login")

    problem = contest.problem(name)
    if problem is None:
        return abort(404)

    subs = list(Submission.from_user_and_problem_and_contest(current_user, problem, contest))

    return render_template("problem.html", problem=problem, contest=contest, user=current_user, submissions=subs)


@root.route("/<contest_name>/<name>.zip")
@root.route("/<contest_name>/<name>/assets/<path:path>")
def files(contest_name, name, path=None):
    contest = Contest.contest(contest_name)
    problem = contest.problem(name)
    user = get_current_user(contest_name)
    if user is None:
        return redirect("user.login")
    if problem is None or contest is None:
        return abort(404)
    if path is None:
        return send_file(problem.files_zip)
    return send_file(os.path.join(problem.path, "assets", path))


@root.route('/<contest>/<problem>/<int:timestamp>')
def submission_view(contest, problem, timestamp):
    time = datetime.fromtimestamp(timestamp)
    user = get_current_user(contest)
    contest = Contest(contest)
    problem = contest.problem(problem)
    submission = Submission(contest, problem, user, time)
    if not submission.exists:
        return abort(404)

    return render_template('submission.html', goals=submission.problem.goals, user=user, submission=submission, contest=contest)


@root.route('/<contest>/<problem>/<int:timestamp>/<filename>')
def submission_download(contest, problem, timestamp, filename):
    time = datetime.fromtimestamp(timestamp)
    user = get_current_user(contest)
    contest = Contest(contest)
    problem = contest.problem(problem)
    submission = Submission(contest, problem, user, time)
    if not submission.exists or filename not in submission.files.values():
        return abort(404)
    return send_file(os.path.join(submission.path, filename))
