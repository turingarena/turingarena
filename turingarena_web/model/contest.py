from collections import namedtuple

from turingarena_web.model.database import database
from turingarena_web.model.problem import Problem
from turingarena_web.model.user import User


class Contest(namedtuple("Contest", ["id", "name", "public", "allowed_languages"])):
    @property
    def users(self):
        return User.from_contest(self)

    @property
    def problems(self):
        return Problem.from_contest(self)

    def add_user(self, username):
        query = """
            INSERT INTO user_contest(user_id, contest_id) VALUES (
                (SELECT id FROM _user WHERE username = %s),
                %s
            )
        """
        database.query(query, username, self.id)

    def remove_user(self, username):
        query = """
            DELETE FROM user_contest 
            WHERE contest_id = %s AND user_id = (SELECT id FROM _user WHERE username = %s)
        """
        database.query(query, self.id, username)

    def contains_user(self, user):
        query = "SELECT 1 FROM user_contest WHERE contest_id = %s AND user_id = %s"
        return database.query_exists(query, self.id, user.id)

    def add_problem(self, problem_name):
        query = """
            INSERT INTO problem_contest(problem_id, contest_id) VALUES (
                (SELECT id FROM problem WHERE name = %s),
                %s
            )
        """
        database.query(query, problem_name, self.id)

    def remove_problem(self, problem_name):
        query = """
            DELETE FROM problem_contest 
            WHERE contest_id = %s AND problem_id = (SELECT id FROM problem WHERE name = %s)
        """
        database.query(query, self.id, problem_name)

    def contains_problem(self, problem: Problem):
        query = "SELECT 1 FROM problem_contest WHERE contest_id = %s AND problem_id = %s"
        return database.query_exists(query, self.id, problem.id)

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
    def contests():
        query = "SELECT * FROM contest"
        return database.query_all(query, convert=Contest)

    @staticmethod
    def new_contest(contest_name, public=False, allowed__languages=[]):
        query = "INSERT INTO contest(name, public, allowed_languages) VALUES (%s, %s, %s)"
        database.query(query, contest_name, public, allowed__languages)

    @staticmethod
    def delete_contest(contest_name):
        query = "DELETE FROM contest WHERE name = %s"
        database.query(query, contest_name)

    @staticmethod
    def exists_with_user_and_problem(user, problem):
        query = """
            SELECT 1 
            FROM contest c JOIN user_contest uc ON c.id = uc.contest_id JOIN problem_contest pc ON c.id = pc.contest_id
            WHERE uc.user_id = %s AND pc.problem_id = %s
        """
        return database.query_exists(query, user.id, problem.id)
