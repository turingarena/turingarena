from collections import namedtuple
from enum import Enum

from turingarena_web.config import config
from turingarena_web.database import database
from turingarena_web.user import User
from turingarena_web.problem import Problem, Goal


class EvaluationEventType(Enum):
    TEXT = "TEXT"
    DATA = "DATA"
    END = "END"


class EvaluationEvent(namedtuple("EvaluationEvent", ["submission_id", "serial", "type_", "data"])):
    @property
    def type(self):
        return EvaluationEventType(self.type_)

    @staticmethod
    def from_submission(submission):
        query = "SELECT * FROM evaluation_event WHERE submission_id = %s ORDER BY serial"
        return database.query_all(query, submission.id, convert=EvaluationEvent)

    @staticmethod
    def insert(submission, event_type, payload):
        query = "INSERT INTO evaluation_event(submission_id, type, data) VALUES (%s, %s, %s) RETURNING *"
        return database.query_one(query, submission.id, event_type, payload, convert=EvaluationEvent)


class Submission(namedtuple("Submission", ["id", "problem_id", "user_id", "timestamp", "filename"])):
    @staticmethod
    def from_user_and_problem(user, problem):
        query = "SELECT * FROM submission WHERE user_id = %s AND problem_id = %s ORDER BY timestamp DESC"
        return database.query_all(query, user.id, problem.id, convert=Submission)

    @staticmethod
    def from_id(submission_id):
        query = "SELECT * FROM submission WHERE id = %s"
        return database.query_one(query, submission_id, convert=Submission)

    @staticmethod
    def new(user, problem, filename):
        query = "INSERT INTO submission(problem_id, user_id, filename) VALUES (%s, %s, %s) RETURNING *"
        return database.query_one(query, problem.id, user.id, filename, convert=Submission)

    @property
    def problem(self):
        return Problem.from_id(self.problem_id)

    @property
    def user(self):
        return User.from_id(self.user_id)

    @property
    def path(self):
        return config["submitted_file_path"].format(
            problem_name=self.problem.name,
            username=self.user.username,
            timestamp=str(self.timestamp).replace(' ', '_'),
            filename=self.filename
        )

    @property
    def goals(self):
        goals = {
            goal: False
            for goal in self.problem.goals
        }

        for goal in Goal.from_submission(self):
            goals[goal] = True

        return goals

    @property
    def events(self):
        return EvaluationEvent.from_submission(self)

    def event(self, event_type, payload):
        return EvaluationEvent.insert(self, event_type, payload)
