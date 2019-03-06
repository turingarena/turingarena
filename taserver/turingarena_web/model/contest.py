import os

from collections import namedtuple

from turingarena.evallib.metadata import load_metadata
from turingarena_web.model.database import database
from turingarena_web.model.problem import Problem
from turingarena_web.model.user import User
from turingarena_web.config import config


class Contest(namedtuple("Contest", ["id", "name", "title", "public", "allowed_languages"])):
    @property
    def directory(self):
        return os.path.join(config.contest_dir_path.format(name=self.name))

    @property
    def metadata(self):
        return load_metadata(self.directory)

    @property
    def users(self):
        return User.from_contest(self)

    @property
    def problems(self):
        problems = [
            os.path.join(self.directory, path)
            for path in os.listdir(self.directory)
        ]
        return [
            Problem(path)
            for path in problems
            if os.path.isdir(path)
        ]

    def problem(self, name):
        path = os.path.join(self.directory, name)
        if not os.path.isdir(path):
            return None
        return Problem(path)

    def add_user(self, user):
        query = "INSERT INTO user_contest(user_id, contest_id) VALUES (%s, %s)"
        database.query(query, user.id, self.id)

    def remove_user(self, user):
        query = "DELETE FROM user_contest WHERE contest_id = %s AND user_id = %s"
        database.query(query, self.id, user.id)

    def contains_user(self, user):
        query = "SELECT 1 FROM user_contest WHERE contest_id = %s AND user_id = %s"
        return database.query_exists(query, self.id, user.id)

    def add_language(self, language):
        query = "UPDATE contest SET allowed_languages = array_append(allowed_languages, %s) WHERE id = %s"
        database.query(query, language, self.id)

    def remove_language(self, language):
        query = "UPDATE contest SET allowed_languages = array_remove(allowed_languages, %s) WHERE id = %s"
        database.query(query, language, self.id)

    @staticmethod
    def of_user(user):
        query = """
            SELECT c.*
            FROM contest c JOIN user_contest uc ON c.id = uc.contest_id
            WHERE uc.user_id = %s
        """
        return database.query_all(query, user.id, convert=Contest)

    @staticmethod
    def from_name(contest_name):
        query = "SELECT * FROM contest WHERE name = %s"
        return database.query_one(query, contest_name, convert=Contest)

    @staticmethod
    def from_id(contest_id):
        query = "SELECT * FROM contest WHERE id = %s"
        return database.query_one(query, contest_id, convert=Contest)

    @staticmethod
    def contests():
        query = "SELECT * FROM contest"
        return database.query_all(query, convert=Contest)

    @staticmethod
    def new_contest(contest_name, title=None, public=False, allowed__languages=[]):
        if title is None:
            title = contest_name
        query = "INSERT INTO contest(name, title, public, allowed_languages) VALUES (%s, %s, %s, %s) RETURNING *"
        contest = database.query_one(query, contest_name, title, public, allowed__languages, convert=Contest)
        os.makedirs(contest.directory)

    @staticmethod
    def delete_contest(contest_name):
        query = "DELETE FROM contest WHERE name = %s"
        database.query(query, contest_name)
