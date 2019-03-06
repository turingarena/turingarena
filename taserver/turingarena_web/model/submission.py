import json

from collections import namedtuple
from enum import Enum

from turingarena.evaluation.events import EvaluationEventType, EvaluationEvent

from turingarena_web.config import config
from turingarena_web.model.contest import Contest
from turingarena_web.model.database import database
from turingarena_web.model.user import User


class SubmissionStatus(Enum):
    EVALUATING = "EVALUATING"
    EVALUATED = "EVALUATED"
    RECEIVED = "RECEIVED"


class Submission(namedtuple("Submission", ["id", "problem_name", "contest_name", "user_id", "timestamp", "filename", "status_"])):
    @staticmethod
    def from_user_and_problem_and_contest(user, problem, contest):
        query = "SELECT * FROM submission WHERE user_id = %s AND problem = %s AND contest = %s ORDER BY timestamp DESC"
        return database.query_all(query, user.id, problem.name, contest.name, convert=Submission)

    @staticmethod
    def from_id(submission_id):
        query = "SELECT * FROM submission WHERE id = %s"
        return database.query_one(query, submission_id, convert=Submission)

    @staticmethod
    def new(user, problem, contest, filename):
        query = "INSERT INTO submission(problem, contest, user_id, filename) VALUES (%s, %s, %s, %s) RETURNING *"
        return database.query_one(query, problem.name, contest.name, user.id, filename, convert=Submission)

    @property
    def status(self):
        return SubmissionStatus(self.status_)

    @property
    def problem(self):
        return self.contest.problem(self.problem_name)

    @property
    def contest(self):
        return Contest.contest(self.contest_name)

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
            event.payload
            for event in self.events()
            if event.type == EvaluationEventType.DATA and event.payload["type"] == "goal_result"
        ]

    @property
    def acquired_goals(self):
        return [
            goal
            for goal in self.goals
            if goal["result"]
        ]

    def events(self, after=0):
        query = f"SELECT type, data FROM evaluation_event WHERE submission_id = %s AND serial > %s ORDER BY serial"
        for event_type, payload in database.query_all(query, self.id, after):
            event_type = EvaluationEventType(event_type.lower())
            if event_type != EvaluationEventType.TEXT:
                payload = json.loads(payload)
            yield EvaluationEvent(event_type, payload)

    def event(self, event_type, payload):
        query = "INSERT INTO evaluation_event(submission_id, type, data) VALUES (%s, %s, %s) RETURNING *"
        if event_type != 'text':
            payload = json.dumps(payload)
        database.query_one(query, self.id, event_type.upper(), payload)

    def set_status(self, status):
        query = "UPDATE submission SET status = %s WHERE id = %s"
        database.query(query, status.value, self.id)

    def as_json_data(self):
        return {
            "id": self.id,
            "user": self.user.username,
            "problem": self.problem.name,
            "contest": self.contest.name,
            "timestamp": self.timestamp,
            "filename": self.filename,
            "status": self.status.value,
        }
