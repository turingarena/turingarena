import json

from collections import namedtuple
from enum import Enum

from turingarena.evaluation.events import EvaluationEventType

from turingarena_web.config import config
from turingarena_web.model.contest import Contest
from turingarena_web.model.database import database
from turingarena_web.model.user import User


class EvaluationEvent(namedtuple("EvaluationEvent", ["submission_id", "serial", "type_", "data"])):
    @property
    def type(self):
        return EvaluationEventType(self.type_.lower())

    @property
    def payload(self):
        if self.type == EvaluationEventType.TEXT:
            return str(self.data)
        else:
            return json.loads(self.data)

    @staticmethod
    def from_submission(submission, event_type=None, after=0):
        if event_type is None:
            t = ""
        else:
            t = f"AND type = '{event_type.value.upper()}'"
        query = f"SELECT * FROM evaluation_event WHERE submission_id = %s {t} AND serial > %s ORDER BY serial"
        return database.query_all(query, submission.id, after, convert=EvaluationEvent)

    @staticmethod
    def insert(submission, event_type, payload):
        query = "INSERT INTO evaluation_event(submission_id, type, data) VALUES (%s, %s, %s) RETURNING *"
        if event_type != 'text':
            payload = json.dumps(payload)
        return database.query_one(query, submission.id, event_type.upper(), payload, convert=EvaluationEvent)


class SubmissionStatus(Enum):
    EVALUATING = "EVALUATING"
    EVALUATED = "EVALUATED"
    RECEIVED = "RECEIVED"


class Submission(namedtuple("Submission", ["id", "problem_name", "contest_id", "user_id", "timestamp", "filename", "status_"])):
    @staticmethod
    def from_user_and_problem_and_contest(user, problem, contest):
        query = "SELECT * FROM submission WHERE user_id = %s AND problem = %s AND contest_id = %s ORDER BY timestamp DESC"
        return database.query_all(query, user.id, problem.name, contest.id, convert=Submission)

    @staticmethod
    def from_id(submission_id):
        query = "SELECT * FROM submission WHERE id = %s"
        return database.query_one(query, submission_id, convert=Submission)

    @staticmethod
    def new(user, problem, contest, filename):
        query = "INSERT INTO submission(problem, contest_id, user_id, filename) VALUES (%s, %s, %s, %s) RETURNING *"
        return database.query_one(query, problem.name, contest.id, user.id, filename, convert=Submission)

    @property
    def status(self):
        return SubmissionStatus(self.status_)

    @property
    def problem(self):
        return self.contest.problem(self.problem_name)

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
        return [
            dict(name=event.payload["name"], result=event.payload["result"])
            for event in EvaluationEvent.from_submission(self, event_type=EvaluationEventType.DATA)
            if event.payload["type"] == "goal_result"
        ]

    @property
    def acquired_goals(self):
        return [
            goal
            for goal in self.goals
            if goal["result"]
        ]

    def event(self, event_type, payload):
        return EvaluationEvent.insert(self, event_type.value, payload)

    def set_status(self, status):
        query = "UPDATE submission SET status = %s WHERE id = %s"
        database.query(query, status.value, self.id)
