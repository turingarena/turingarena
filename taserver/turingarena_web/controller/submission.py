from flask import Blueprint, render_template, send_file, abort
from turingarena_web.model.submission import Submission
from turingarena_web.controller.session import get_current_user

submission_bp = Blueprint('submission', __name__)


@submission_bp.route('/<int:submission_id>')
def submission_view(submission_id):
    current_user = get_current_user()
    submission = Submission.from_id(submission_id)
    if submission is None or current_user is None or current_user.id != submission.user.id:
        return abort(404)

    return render_template('submission.html', goals=submission.problem.goals, user=current_user, id=submission.id)


@submission_bp.route('/<int:submission_id>/<string:filename>')
def download(submission_id, filename):
    submission = Submission.from_id(submission_id)
    user = get_current_user()
    if submission is None or user is None or user.id != submission.user_id or submission.filename == filename:
        return abort(404)
    return send_file(submission.path)
