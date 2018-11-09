from turingarena.evaluation.evaluator import Evaluator

from turingarena_web.database import Problem, EvaluationEventDatabase


def evaluate(problem: Problem, submission, app):
    with app.app_context():
        ee_database = EvaluationEventDatabase()

        evaluator = Evaluator(problem.path)
        submission_files = dict(
            source=submission.path
        )

        for event in evaluator.evaluate(files=submission_files):
            ee_database.insert(submission_id=submission.id, e_type=event.type.value.upper(), data=str(event.payload))
