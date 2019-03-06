import os
import threading

from turingarena.driver.language import Language
from turingarena.evaluation.evaluator import Evaluator
from turingarena.evaluation.events import EvaluationEventType, EvaluationEvent

from turingarena_web.model.submission import Submission, SubmissionStatus


def evaluate_thread(problem, submission):
    evaluator = Evaluator(problem.path)
    submission_files = dict(
        source=submission.source_path
    )

    submission.set_status(SubmissionStatus.EVALUATING)
    with open(submission.events_path, "w") as f:
        for event in evaluator.evaluate(files=submission_files, redirect_stderr=True, log_level="WARNING"):
            print(event.json_line(), file=f, flush=True)

        print(EvaluationEvent(EvaluationEventType.DATA, payload=dict(type="end")).json_line(), file=f, flush=True)
    submission.set_status(SubmissionStatus.EVALUATED)


def evaluate(current_user, problem, contest, submitted_file):

    ext = os.path.splitext(submitted_file["filename"])[1]

    language = Language.from_extension(ext)
    if language not in contest.languages:
        raise RuntimeError(f"Unsupported file extension {ext}: please select another file!")

    submission = Submission.new(current_user, problem, contest, submitted_file["filename"])

    os.makedirs(submission.path)

    with open(submission.source_path, "w") as f:
        f.write(submitted_file["content"])

    threading.Thread(target=evaluate_thread, args=(problem, submission)).start()

    return submission
