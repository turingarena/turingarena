import threading

from turingarena.evaluation.evaluator import Evaluator
from turingarena.evaluation.events import EvaluationEventType, EvaluationEvent

from turingarena_web.model.submission import Submission


def evaluate_thread(problem, submission):
    evaluator = Evaluator(problem.path)
    with open(submission.events_path, "w") as f:
        for event in evaluator.evaluate(files=submission.files_absolute, redirect_stderr=True, log_level="WARNING"):
            print(event.json_line(), file=f, flush=True)

        print(EvaluationEvent(EvaluationEventType.DATA, payload=dict(type="end")).json_line(), file=f, flush=True)


def evaluate(current_user, problem, contest, files):

    for name, file in files.items():
        if file.language not in contest.languages:
            raise RuntimeError(f"Unsupported file extension {file.extension}: please select another file!")

    submission = Submission.new(current_user, problem, contest, files)

    threading.Thread(target=evaluate_thread, args=(problem, submission)).start()

    return submission
