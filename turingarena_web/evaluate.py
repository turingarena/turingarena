from turingarena.evaluation.evaluator import Evaluator
from turingarena.evaluation.submission import SubmissionFile

from turingarena_web.database import Submission, Problem, EvaluationEventDatabase

ee_database = EvaluationEventDatabase()


def evaluate(problem: Problem, submission: Submission):
    evaluator = Evaluator(problem.path)
    with open(submission.path) as f:
        content = f.read()
    submission_files = dict(
        source=SubmissionFile(
            filename=submission.filename,
            content=content,
        )
    )

    for event in evaluator.evaluate(files=submission_files):
        ee_database.insert(submission_id=submission.id, type=event.type.upper(), data=event.data)
