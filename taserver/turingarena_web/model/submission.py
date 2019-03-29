import subprocess

import os
import json

from datetime import datetime
from functools import lru_cache
from collections import namedtuple

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
            ext = os.path.splitext(file["filename"])[1]
            if ext not in contest.languages:
                raise RuntimeError(f"Unsupported file extension {ext}: please select another file!")

        submission = Submission(
            contest=contest,
            problem=problem,
            user=user,
            time=datetime.now(),
        )

        os.makedirs(submission.path)

        for file in files.values():
            with open(os.path.join(submission.path, file["filename"]), "w") as f:
                f.write(file["content"])

        files = {
            name: file["filename"]
            for name, file in files.items()
        }

        with open(os.path.join(submission.path, "files.json"), "w") as f:
            print(json.dumps(files), file=f)

        submission.evaluate()

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
        return {
            event["name"]: event["result"]
            for event in self.events()
            if event.type == "goal_result"
        }

    def events(self, after=-1):
        with open(self.events_path) as f:
            i = 0
            for line in f:
                if i > after:
                    yield json.loads(line)
                i += 1

    def evaluate(self):
        files = [
            f"{name}:{filename}"
            for name, filename in self.files_absolute.items()
        ]
        with open(self.events_path, "w") as f:
            subprocess.Popen(["turingarena-dev", "evaluate", "--events"] + files, stdout=f, cwd=self.problem.path)

    def as_json_data(self):
        return {
            "user": self.user.username,
            "problem": self.problem.name,
            "contest": self.contest.name,
            "timestamp": self.timestamp,
            "files": self.files,
        }
