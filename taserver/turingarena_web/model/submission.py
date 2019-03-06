import json
import os

from collections import namedtuple

from turingarena.evaluation.events import EvaluationEventType, EvaluationEvent

from turingarena_web.config import config
from turingarena_web.model.contest import Contest
from turingarena_web.model.database import database
from turingarena_web.model.user import User


class Submission(namedtuple("Submission", ["id", "problem_name", "contest_name", "user_id", "timestamp", "filename"])):
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
        return config.submission_dir_path.format(
            problem_name=self.problem.name,
            username=self.user.username,
            timestamp=self.timestamp,
            contest_name=self.contest.name
        )

    @property
    def files(self):
        return {
            "source": self.filename
        }

    @property
    def files_absolute(self):
        return {
            name: os.path.join(self.path, filename)
            for name, filename in self.files.items()
        }

    @property
    def events_path(self):
        return os.path.join(self.path, "events.jsonl")

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

    def events(self, after=-1):
        with open(self.events_path) as f:
            i = 0
            for line in f:
                if i > after:
                    yield EvaluationEvent.from_json(json.loads(line))
                i += 1

    def as_json_data(self):
        return {
            "id": self.id,
            "user": self.user.username,
            "problem": self.problem.name,
            "contest": self.contest.name,
            "timestamp": self.timestamp,
            "files": self.files,
        }
