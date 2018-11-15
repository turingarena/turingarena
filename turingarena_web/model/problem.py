import logging
import os
import shutil
import subprocess
from collections import namedtuple

from commonmark import commonmark
from turingarena.evallib.metadata import load_metadata
from turingarena.file.generated import PackGeneratedDirectory

from turingarena_web.config import config
from turingarena_web.model.database import database


class Goal(namedtuple("Goal", ["id", "problem_id", "name"])):
    @property
    def problem(self):
        return Problem.from_id(self.problem_id)

    @staticmethod
    def from_submission(submission):
        query = "SELECT g.* FROM goal g JOIN acquired_goal ag ON g.id = ag.goal_id WHERE ag.submission_id = %s"
        return database.query_all(query, submission.id, convert=Goal)

    @staticmethod
    def insert(problem, name):
        query = "INSERT INTO goal(problem_id, name) VALUES (%s, %s) RETURNING *"
        return database.query_one(query, problem.id, name, convert=Goal)

    def acquire(self, submission):
        query = "INSERT INTO acquired_goal(submission_id, goal_id) VALUES (%s, %s)"
        database.query(query, submission.id, self.id)

    @staticmethod
    def from_problem_and_name(problem, name):
        query = "SELECT * FROM goal WHERE problem_id = %s AND name = %s"
        return database.query_one(query, problem.id, name, convert=Goal)


class Problem(namedtuple("Problem", ["id", "name", "title", "location"])):
    def statement(self, contest):
        path = os.path.join(self.files_dir(contest), ".generated", "statement.md")
        with open(path) as f:
            return commonmark(f.read())

    def zip_path(self, contest):
        return os.path.join(self.files_dir(contest), f"{self.name}.zip")

    def files_dir(self, contest):
        return os.path.join(self.path, "files", contest.name)

    @property
    def metadata(self):
        return load_metadata(self.path)

    @property
    def path(self):
        return config.problem_dir_path.format(name=self.name)

    @property
    def goals(self):
        query = "SELECT * FROM goal WHERE problem_id = %s"
        return database.query_all(query, self.id, convert=Goal)

    @property
    def n_goals(self):
        query = "SELECT COUNT(*) FROM goal WHERE problem_id = %s"
        return database.query_one(query, self.id, convert=int)

    @property
    def contests(self):
        from turingarena_web.model.contest import Contest
        return Contest.with_problem(self)

    def goal(self, name):
        return Goal.from_problem_and_name(self, name)

    def max_goals_of_user_in_contest(self, user, contest):
        query = """
            SELECT MAX(n_goals) FROM (
                SELECT COUNT(*) AS n_goals, s.id 
                FROM acquired_goal ac JOIN submission s ON ac.submission_id = s.id 
                GROUP BY s.id
                HAVING s.contest_id = %s AND s.user_id = %s and s.problem_id = %s
            ) AS goals_of_submission
        """
        return database.query_one(query, contest.id, user.id, self.id, convert=lambda x: 0 if x is None else int(x))

    @staticmethod
    def problems():
        query = "SELECT * FROM problem"
        return database.query_all(query, convert=Problem)

    @staticmethod
    def from_name(name):
        query = "SELECT * FROM problem WHERE name = %s"
        return database.query_one(query, name, convert=Problem)

    @staticmethod
    def from_id(problem_id):
        query = "SELECT * FROM problem WHERE id = %s"
        return database.query_one(query, problem_id, convert=Problem)

    @staticmethod
    def from_contest(contest):
        query = """
            SELECT p.id, p.name, p.title, p.location
            FROM problem p JOIN problem_contest pc ON p.id = pc.problem_id
            WHERE pc.contest_id = %s 
        """
        return database.query_all(query, contest.id, convert=Problem)

    def delete_files(self, contest):
        shutil.rmtree(self.files_dir(contest), ignore_errors=True)

    @staticmethod
    def install(location, name=None, title=None):
        if name is None:
            name = os.path.basename(location)
        if title is None:
            title = name

        query = "INSERT INTO problem(name, title, location) VALUES (%s, %s, %s) RETURNING *"
        problem = Problem(*database.query_one(query, name, title, location))
        problem._git_clone()
        scoring_metadata = problem.metadata.get("scoring", {})
        goals = scoring_metadata.get("goals", [])

        for goal in goals:
            Goal.insert(problem, goal)

        return problem

    def delete(self):
        subprocess.call(["rm", "-rf", self.path])
        database.query("DELETE FROM problem WHERE id = %s", self.id)

    def update(self):
        os.chdir(self.path)
        subprocess.call(["git", "pull"])
        for contest in self.contests:
            self.update_files(contest)

    def _git_clone(self):
        os.mkdir(self.path)
        logging.debug(f"git clone {self.location} -> {self.path}")
        subprocess.call(["git", "clone", self.location, self.path])

    def update_files(self, contest):
        logging.info(f"Generating file for contest {contest}")
        self.delete_files(contest)
        files_dir = os.path.join(self.files_dir(contest), ".generated")
        os.makedirs(files_dir)
        pd = PackGeneratedDirectory(self.path, allowed_languages=contest.allowed_languages)

        for path, generator in pd.targets:
            directory = os.path.join(files_dir, os.path.split(path)[0])
            filename = os.path.split(path)[1]
            os.makedirs(directory, exist_ok=True)
            with open(os.path.join(directory, filename), "w") as file:
                generator(file)

        os.chdir(files_dir)
        subprocess.call(["zip", "-r", self.zip_path(contest), "."])
