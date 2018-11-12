import os
import threading
from datetime import datetime

from flask import request, current_app, redirect, url_for
from turingarena.driver.language import Language
from turingarena.evaluation.evaluator import Evaluator
from turingarena.evaluation.events import EvaluationEventType

from turingarena_web.database import Problem, database
from turingarena_web.views.submission import submitted_file_path


def available_languages():
    if "ALLOWED_LANGUAGES" in current_app.config:
        return [
            Language.from_name(lang)
            for lang in current_app.config["ALLOWED_LANGUAGES"]
        ]
    return Language.languages()


def available_extensions():
    return [
        lang.extension
        for lang in available_languages()
    ]


def evaluate_thread(problem: Problem, submission, app):
    with app.app_context():
        evaluator = Evaluator(problem.path)
        submission_files = dict(
            source=submission.path
        )

        for event in evaluator.evaluate(files=submission_files, redirect_stderr=True):
            if event.type == EvaluationEventType.DATA:
                data = event.payload
                if "type" in data and data["type"] == "goal_result":
                    goal_name = data["goal"]
                    result = data["result"]
                    if result:
                        database.insert_goal(submission=submission, name=goal_name)

            database.insert_evaluation_event(submission_id=submission.id, e_type=event.type.value.upper(), data=str(event.payload))

        database.insert_evaluation_event(submission_id=submission.id, e_type="END", data=None)


def evaluate(current_user, problem):
    timestamp = datetime.now()
    submitted_file = request.files["source"]

    ext = os.path.splitext(submitted_file.filename)[1]

    if ext not in available_extensions():
        raise RuntimeError(f"Unsupported file extension {ext}: please select another file!")

    path = submitted_file_path(
        problem_name=problem.name,
        username=current_user.username,
        timestamp=timestamp,
        filename=submitted_file.filename,
    )

    os.makedirs(os.path.split(path)[0], exist_ok=True)
    submitted_file.save(path)

    submission_id = database.insert_submission(
        user_id=current_user.id,
        problem_id=problem.id,
        filename=submitted_file.filename,
        path=path,
    )
    submission = database.get_submission_by_id(submission_id)

    threading.Thread(target=evaluate_thread, args=(problem, submission, current_app._get_current_object())).start()

    return redirect(url_for("submission.submission_view", submission_id=submission_id))
