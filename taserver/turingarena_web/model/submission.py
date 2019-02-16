from collections import namedtuple
from enum import Enum

from turingarena.evaluation.events import EvaluationEventType

from turingarena_web.config import config
from turingarena_web.model.contest import Contest
from turingarena_web.model.database import database
from turingarena_web.model.user import User
from turingarena_web.model.problem import Problem, Goal


class EvaluationEvent(namedtuple("EvaluationEvent", ["submission_id", "serial", "type_", "data"])):
    @property
    def type(self):
        return EvaluationEventType(self.type_.lower())

    @staticmethod
    def from_submission(submission, event_type=EvaluationEventType.TEXT):
        query = "SELECT * FROM evaluation_event WHERE submission_id = %s AND type = %s ORDER BY serial"
        return database.query_all(query, submission.id, event_type.value.upper(), convert=EvaluationEvent)

    @staticmethod
    def insert(submission, event_type, payload):
        query = "INSERT INTO evaluation_event(submission_id, type, data) VALUES (%s, %s, %s) RETURNING *"
        return database.query_one(query, submission.id, event_type.upper(), payload, convert=EvaluationEvent)


class SubmissionStatus(Enum):
    EVALUATING = "EVALUATING"
    EVALUATED = "EVALUATED"
    RECEIVED = "RECEIVED"


class Submission(namedtuple("Submission", ["id", "problem_id", "contest_id", "user_id", "timestamp", "filename", "status_"])):
    @staticmethod
    def from_user_and_problem_and_contest(user, problem, contest):
        query = "SELECT * FROM submission WHERE user_id = %s AND problem_id = %s AND contest_id = %s ORDER BY timestamp DESC"
        return database.query_all(query, user.id, problem.id, contest.id, convert=Submission)

    @staticmethod
    def from_id(submission_id):
        query = "SELECT * FROM submission WHERE id = %s"
        return database.query_one(query, submission_id, convert=Submission)

    @staticmethod
    def new(user, problem, contest, filename):
        query = "INSERT INTO submission(problem_id, contest_id, user_id, filename) VALUES (%s, %s, %s, %s) RETURNING *"
        return database.query_one(query, problem.id, contest.id, user.id, filename, convert=Submission)

    @property
    def status(self):
        return SubmissionStatus(self.status_)

    @property
    def problem(self):
        return Problem.from_id(self.problem_id)

    @property
    def contest(self):
        return Contest.from_id(self.contest_id)

    @property
    def user(self):
        return User.from_id(self.user_id)

    @property
    def path(self):
        return config.submitted_file_path.format(
            problem_name=self.problem.name,
            username=self.user.username,
            timestamp=str(self.timestamp).replace(' ', '_'),
            filename=self.filename,
            contest_name=self.contest.name
        )

    @property
    def goals(self):
        goals = {
            goal: None
            for goal in self.problem.goals
        }

        for goal, result in Goal.from_submission(self):
            goals[goal] = result

        return goals

    @property
    def text_events(self):
        return EvaluationEvent.from_submission(self, event_type=EvaluationEventType.TEXT)

    @property
    def file_events(self):
        return EvaluationEvent.from_submission(self, event_type=EvaluationEventType.FILE)

    def event(self, event_type, payload):
        return EvaluationEvent.insert(self, event_type.value, payload)

    def set_status(self, status):
        query = "UPDATE submission SET status = %s WHERE id = %s"
        database.query(query, status.value, self.id)
