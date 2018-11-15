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

    def add_problem(self, problem):
        query = """
            INSERT INTO problem_contest(problem_id, contest_id) VALUES (%s, %s)
        """
        database.query(query, problem.id, self.id)
        problem.update_files(self)

    def add_language(self, language):
        query = "UPDATE contest SET allowed_languages = array_append(allowed_languages, %s) WHERE id = %s"
        database.query(query, language, self.id)

    def remove_language(self, language):
        query = "UPDATE contest SET allowed_languages = array_remove(allowed_languages, %s) WHERE id = %s"
        database.query(query, language, self.id)

    def remove_problem(self, problem):
        query = """
            DELETE FROM problem_contest WHERE contest_id = %s AND problem_id = %s
        """
        database.query(query, self.id, problem.id)
        problem.delete_files(self)

    def contains_problem(self, problem: Problem):
        query = "SELECT 1 FROM problem_contest WHERE contest_id = %s AND problem_id = %s"
        return database.query_exists(query, self.id, problem.id)

    def user_score(self, user):
        problem_solved = 0
        total_goals = 0
        solved_goals = 0
        for problem in self.problems:
            n_goals = problem.n_goals
            correct_goals = problem.max_goals_of_user_in_contest(user, self)
            if correct_goals == n_goals and n_goals != 0:
                problem_solved += 1
            total_goals += n_goals
            solved_goals += correct_goals
        return problem_solved, solved_goals, total_goals

    @property
    def scoreboard(self):
        n_problems = len(list(self.problems))
        board = []
        for user in self.users:
            solved, goals, total = self.user_score(user)
            board.append((user.username, solved, goals, total))
        board.sort(key=lambda x: x[1])
        return [
            (username, f"{s}/{n_problems}", f"{g}/{t}")
            for username, s, g, t in board
        ]

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

    @staticmethod
    def with_problem(problem):
        query = "SELECT c.* FROM contest c JOIN problem_contest pc ON c.id = pc.contest_id WHERE pc.problem_id = %s"
        return database.query_all(query, problem.id, convert=Contest)
