import sys

from turingarena.evaluation.evaluator import Evaluator
from turingarena.evaluation.events import EvaluationEventType

from turingarena_web.database import Problem, database


def evaluate(problem: Problem, submission, app):
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

