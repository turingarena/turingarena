from flask import Blueprint, render_template

submission = Blueprint('submission', __name__)


@submission.route('/<id>')
def submission_view(id):
    # TODO: get submission from database
    return render_template('submission.html')