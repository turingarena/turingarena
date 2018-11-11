from flask import Blueprint, render_template, current_app, send_file, abort

from turingarena_web.database import database
from turingarena_web.user import get_current_user

submission = Blueprint('submission', __name__)


def submitted_file_path(*, problem_name, username, timestamp, filename):
    return current_app.config["SUBMITTED_FILE_PATH"].format(
        problem_name=problem_name,
        username=username,
        timestamp=str(timestamp).replace(' ', '_'),
        filename=filename
    )


@submission.route('/<int:submission_id>')
def submission_view(submission_id):
    current_user = get_current_user()
    sub = database.get_submission_by_id(submission_id)
    if current_user is None or current_user.id != sub.user_id:
        return abort(403)
    end = False
    events = []
    for event in database.get_all_evaluation_events(submission_id):
        if event.type == "TEXT":
            events.append(event)
        if event.type == "END":
            end = True
    goals = database.get_goals(submission_id)

    return render_template('submission.html', events=events, end=end, goals=goals, user=current_user)


@submission.route('/<int:submission_id>/<string:filename>')
def download(submission_id, filename):
    sub = database.get_submission_by_id(submission_id)
    if get_current_user().id != sub.user_id:
        return abort(403)
    assert sub.filename == filename
    return send_file(sub.path)
