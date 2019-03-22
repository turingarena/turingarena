import os
import json
import threading

from datetime import datetime
from functools import lru_cache
from collections import namedtuple

from turingarena.evaluation.events import EvaluationEventType, EvaluationEvent
from turingarena.evaluation.evaluator import Evaluator

from turingarena_web.config import config


class Submission(namedtuple("Submission", ["contest", "problem", "user", "time"])):
    SUBMISSION_TIME_FORMAT = "%Y-%m-%dT%H:%M:%S"

    @staticmethod
    def from_user_and_problem_and_contest(user, problem, contest):
        submissions_dir = os.path.join(config.submission_dir_path, contest.name, problem.name, user.username)
        if not os.path.exists(submissions_dir):
            return []
        return sorted([
            Submission(
                problem=problem,
                contest=contest,
                user=user,
                time=datetime.strptime(timestamp, Submission.SUBMISSION_TIME_FORMAT),
            )
            for timestamp in os.listdir(submissions_dir)
        ], key=lambda x: x.time, reverse=True)

    @staticmethod
    def new(user, problem, contest, files):
        for name, file in files.items():
            if file.language not in contest.languages:
                raise RuntimeError(f"Unsupported file extension {file.extension}: please select another file!")

        submission = Submission(
            contest=contest,
            problem=problem,
            user=user,
            time=datetime.now(),
        )

        os.makedirs(submission.path)

        for file in files.values():
            with open(os.path.join(submission.path, file.filename), "w") as f:
                f.write(file.content)

        files = {
            name: file.filename
            for name, file in files.items()
        }

        with open(os.path.join(submission.path, "files.json"), "w") as f:
            print(json.dumps(files), file=f)

        threading.Thread(target=lambda: submission.evaluate()).start()

        return submission

    @property
    def exists(self):
        return os.path.exists(self.path)

    @property
    def timestamp(self):
        return int(self.time.timestamp())

    @property
    def path(self):
        return os.path.join(
            config.submission_dir_path,
            self.contest.name,
            self.problem.name,
            self.user.username,
            self.time.strftime(self.SUBMISSION_TIME_FORMAT)
        )

    @property
    @lru_cache(None)
    def files(self):
        with open(os.path.join(self.path, "files.json")) as f:
            return json.loads(f.read())

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
        return list(filter(lambda g: g["result"], self.goals))

    def events(self, after=-1):
        with open(self.events_path) as f:
            i = 0
            for line in f:
                if i > after:
                    yield EvaluationEvent.from_json(json.loads(line))
                i += 1

    def evaluate(self):
        evaluator = Evaluator(self.problem.path)
        with open(self.events_path, "w") as f:
            for event in evaluator.evaluate(files=self.files_absolute, redirect_stderr=True, log_level="WARNING"):
                print(event.json_line(), file=f, flush=True)

            print(EvaluationEvent(EvaluationEventType.DATA, payload=dict(type="end")).json_line(), file=f, flush=True)

    def as_json_data(self):
        return {
            "user": self.user.username,
            "problem": self.problem.name,
            "contest": self.contest.name,
            "timestamp": self.time,
            "files": self.files,
        }
