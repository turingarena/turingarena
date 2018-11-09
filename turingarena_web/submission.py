from flask import Blueprint, render_template, current_app

from turingarena_web.database import EvaluationEventDatabase

submission = Blueprint('submission', __name__)
ee_database = EvaluationEventDatabase()

def submitted_file_path(*, problem_name, username, timestamp, filename):
    return current_app.config["SUBMITTED_FILE_PATH"].format(
        problem_name=problem_name,
        username=username,
        timestamp=str(timestamp).replace(' ', '_'),
        filename=filename
    )


@submission.route('/<submission_id>')
def submission_view(submission_id):
    events = [
        event
        for event in ee_database.get_all(submission_id)
        if event.data != "\n"
    ]
    return render_template('submission.html', events=events)
