from flask import Blueprint, render_template, current_app, send_file, abort

from turingarena_web.submission import Submission, EvaluationEventType
from turingarena_web.views.user import get_current_user

submission_bp = Blueprint('submission', __name__)


def submitted_file_path(*, problem_name, username, timestamp, filename):
    return current_app.config["SUBMITTED_FILE_PATH"].format(
        problem_name=problem_name,
        username=username,
        timestamp=str(timestamp).replace(' ', '_'),
        filename=filename
    )


@submission_bp.route('/<int:submission_id>')
def submission_view(submission_id):
    current_user = get_current_user()
    submission = Submission.from_id(submission_id)
    if current_user is None or current_user.id != submission.user.id:
        return abort(403)
    end = False
    events = []
    for event in submission.events:
        if event.type == EvaluationEventType.TEXT:
            events.append(event)
        if event.type == EvaluationEventType.END:
            end = True
    return render_template('submission.html', events=events, end=end, goals=submission.goals, user=current_user)


@submission_bp.route('/<int:submission_id>/<string:filename>')
def download(submission_id, filename):
    sub = Submission.from_id(submission_id)
    if get_current_user().id != sub.user_id:
        return abort(403)
    assert sub.filename == filename
    return send_file(sub.path)
