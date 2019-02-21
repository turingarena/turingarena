import os
import threading

from flask import request, redirect, url_for
from turingarena.driver.language import Language
from turingarena.evaluation.evaluator import Evaluator
from turingarena.evaluation.events import EvaluationEventType

from turingarena_web.model.submission import Submission, SubmissionStatus


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
                goal.acquire(submission, result)

        submission.event(event_type=event.type, payload=event.payload)

    submission.event(event_type=EvaluationEventType.DATA, payload=dict(type="end"))
    submission.set_status(SubmissionStatus.EVALUATED)


def evaluate(current_user, problem, contest):
    submitted_file = request.files["source"]

    ext = os.path.splitext(submitted_file.filename)[1]

    allowed_extensions = [Language.from_name(lang).extension for lang in contest.allowed_languages]
    if ext not in allowed_extensions:
        raise RuntimeError(f"Unsupported file extension {ext}: please select another file!")

    submission = Submission.new(current_user, problem, contest, submitted_file.filename)

    os.makedirs(os.path.split(submission.path)[0], exist_ok=True)
    submitted_file.save(submission.path)

    threading.Thread(target=evaluate_thread, args=(problem, submission)).start()

    return redirect(url_for("submission.submission_view", submission_id=submission.id))
