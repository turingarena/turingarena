from collections import namedtuple

from turingarena_web.database import database, User, Problem


class Contest(namedtuple("Contest", ["id", "name"])):
    @property
    def users(self):
        query = """
            SELECT u.id, u.first_name, u.last_name, u.username, u.email, u.privilege
            FROM _user u JOIN user_contest uc ON u.id = uc.user_id
            WHERE uc.contest_id = %s
        """
        return [
            User(*result)
            for result in database.query_all(query, (self.id,))
        ]

    @property
    def problems(self):
        query = """
            SELECT p.id, p.name, p.title, p.location, p.path
            FROM problem p JOIN problem_contest pc ON p.id = pc.problem_id
            WHERE pc.contest_id = %s 
        """
        return [
            Problem(*result)
            for result in database.query_all(query, (self.id,))
        ]

    def add_user(self, username):
        query = """
            INSERT INTO user_contest(user_id, contest_id) VALUES (
                (SELECT id FROM _user WHERE username = %s),
                %s
            )
        """
        database.query(query, (username, self.id))

    def remove_user(self, username):
        query = """
            DELETE FROM user_contest 
            WHERE contest_id = %s AND user_id = (SELECT id FROM _user WHERE username = %s)
        """
        database.query(query, (self.id, username))

    def add_problem(self, problem_name):
        query = """
            INSERT INTO problem_contest(problem_id, contest_id) VALUES (
                (SELECT id FROM problem WHERE name = %s),
                %s
            )
        """
        database.query(query, (problem_name, self.id))

    def remove_problem(self, problem_name):
        query = """
            DELETE FROM problem_contest 
            WHERE contest_id = %s AND problem_id = (SELECT id FROM problem WHERE name = %s)
        """
        database.query(query, (self.id, problem_name))

    @staticmethod
    def user_contests(username):
        query = """
            SELECT c.id, c.name 
            FROM contest c JOIN user_contest uc ON c.id = uc.contest_id JOIN _user u ON uc.user_id = u.id 
            WHERE u.username = %s
        """
        return [
            Contest(*result)
            for result in database.query_all(query, (username,))
        ]

    @staticmethod
    def from_name(contest_name) -> "Contest":
        query = "SELECT id, name FROM contest WHERE name = %s"
        return Contest(*database.query_one(query, (contest_name,)))

    @staticmethod
    def contests():
        query = "SELECT id, name FROM contest"
        return [
            Contest(*result)
            for result in database.query_all(query)
        ]

    @staticmethod
    def new_contest(contest_name):
        query = "INSERT INTO contest(name) VALUES (%s)"
        database.query(query, (contest_name,))

    @staticmethod
    def delete_contest(contest_name):
        query = "DELETE FROM contest WHERE name = %s"
        database.query(query, (contest_name,))

