from flask import Blueprint, render_template, current_app


submission = Blueprint('submission', __name__)


def submitted_file_path(*, problem_name, username, timestamp, filename):
    return current_app.config["SUBMITTED_FILE_PATH"].format(
        problem_name=problem_name,
        username=username,
        timestamp=str(timestamp).replace(' ', '_'),
        filename=filename
    )


@submission.route('/<id>')
def submission_view(id):
    # TODO: get submission from database
    return render_template('submission.html')
