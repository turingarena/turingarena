import os

from flask import Blueprint, render_template, send_file, abort
from datetime import datetime

from turingarena_web.model.contest import Contest
from turingarena_web.model.submission import Submission
from turingarena_web.controller.session import get_current_user


submission_bp = Blueprint("submission", __name__)


@submission_bp.route('/<contest>/<problem>/<int:timestamp>')
def submission_view(contest, problem, timestamp):
    time = datetime.fromtimestamp(timestamp)
    user = get_current_user()
    contest = Contest(contest)
    problem = contest.problem(problem)
    submission = Submission(contest, problem, user, time)
    if not submission.exists:
        return abort(404)

    return render_template('submission.html', goals=submission.problem.goals, user=user, submission=submission)


@submission_bp.route('/<contest>/<problem>/<int:timestamp>/<filename>')
def download(contest, problem, timestamp, filename):
    time = datetime.fromtimestamp(timestamp)
    user = get_current_user()
    contest = Contest(contest)
    problem = contest.problem(problem)
    submission = Submission(contest, problem, user, time)
    if not submission.exists or filename not in submission.files.values():
        return abort(404)
    return send_file(os.path.join(submission.path, filename))
