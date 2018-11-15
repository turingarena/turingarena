import os
import threading

from flask import request, redirect, url_for
from turingarena.driver.language import Language
from turingarena.evaluation.evaluator import Evaluator
from turingarena.evaluation.events import EvaluationEventType

from turingarena_web.config import config
from turingarena_web.model.submission import Submission, SubmissionStatus


def available_languages():
    if "allowed_languages" in config:
        return [
            Language.from_name(lang)
            for lang in config["allowed_languages"]
        ]
    return Language.languages()


def available_extensions():
    return [
        lang.extension
        for lang in available_languages()
    ]


def evaluate_thread(problem, submission):
    evaluator = Evaluator(problem.path)
    submission_files = dict(
        source=submission.path
    )

    submission.set_status(SubmissionStatus.EVALUATING)
    for event in evaluator.evaluate(files=submission_files, redirect_stderr=True, log_level="WARNING"):
        if event.type == EvaluationEventType.DATA:
            data = event.payload
            if data.get("type") == "goal_result":
                goal = problem.goal(data["goal"])
                result = data["result"]
                if result:
                    goal.acquire(submission)
                continue  # process next event

        submission.event(event_type=event.type, payload=str(event.payload))

    submission.set_status(SubmissionStatus.EVALUATED)


def evaluate(current_user, problem):
    submitted_file = request.files["source"]

    ext = os.path.splitext(submitted_file.filename)[1]

    if ext not in available_extensions():
        raise RuntimeError(f"Unsupported file extension {ext}: please select another file!")

    submission = Submission.new(current_user, problem, submitted_file.filename)

    os.makedirs(os.path.split(submission.path)[0], exist_ok=True)
    submitted_file.save(submission.path)

    threading.Thread(target=evaluate_thread, args=(problem, submission)).start()

    return redirect(url_for("submission.submission_view", submission_id=submission.id))
