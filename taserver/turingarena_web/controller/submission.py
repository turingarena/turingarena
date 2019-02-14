from flask import Blueprint, render_template, send_file, abort

from turingarena_web.model.submission import Submission, EvaluationEventType, SubmissionStatus
from turingarena_web.controller.session import get_current_user

submission_bp = Blueprint('submission', __name__)


@submission_bp.route('/<int:submission_id>')
def submission_view(submission_id):
    current_user = get_current_user()
    submission = Submission.from_id(submission_id)
    if current_user is None or current_user.id != submission.user.id:
        return abort(403)
    end = submission.status == SubmissionStatus.EVALUATED
    events = [
        event.data
        for event in submission.events
        if event.type == EvaluationEventType.TEXT
    ]
    return render_template('submission.html', events=events, end=end, goals=submission.goals, user=current_user)


@submission_bp.route('/<int:submission_id>/<string:filename>')
def download(submission_id, filename):
    sub = Submission.from_id(submission_id)
    if get_current_user().id != sub.user_id:
        return abort(403)
    assert sub.filename == filename
    return send_file(sub.path)
