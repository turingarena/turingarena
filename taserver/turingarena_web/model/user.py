import bcrypt

from enum import Enum
from collections import namedtuple

from turingarena_web.model.contest import Contest
from turingarena_web.model.database import database


class UserPrivilege(Enum):
    STANDARD = "STANDARD"
    ADMIN = "ADMIN"
    TUTOR = "TUTOR"


class User(namedtuple("User", ["id", "first_name", "last_name", "username", "email", "password", "privilege_"])):
    @staticmethod
    def from_username(username):
        query = "SELECT * FROM _user WHERE username = %s"
        return database.query_one(query, username, convert=User)

    @staticmethod
    def from_id(user_id):
        query = "SELECT * FROM _user WHERE id = %s"
        return database.query_one(query, user_id, convert=User)

    @staticmethod
    def from_contest(contest):
        query = "SELECT u.* FROM _user u JOIN user_contest uc on u.id = uc.user_id WHERE uc.contest = %s"
        return database.query_all(query, contest.name, convert=User)

    @staticmethod
    def users():
        query = "SELECT * FROM _user"
        return database.query_all(query, convert=User)

    @staticmethod
    def insert(first_name, last_name, username, email, password):
        query = "INSERT INTO _user(first_name, last_name, username, email, password) VALUES (%s, %s, %s, %s, %s) RETURNING *"
        hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("ascii")
        return database.query_one(query, first_name, last_name, username, email, hashed_password, convert=User)

    @property
    def privilege(self):
        return UserPrivilege(self.privilege_)

    @property
    def contests(self):
        query = "SELECT contest FROM user_contest WHERE user_id = %s"
        return [
            Contest.contest(name)
            for name in database.query_all(query, self.id, convert=lambda x: x)
        ]

    def add_to_contest(self, contest: Contest):
        query = "INSERT INTO user_contest(user_id, contest) VALUES (%s, %s)"
        database.query(query, self.id, contest.name)

    def remove_from_contest(self, contest: Contest):
        query = "DELETE FROM user_contest WHERE contest = %s AND user_id = %s"
        database.query(query, self.id, contest.name)

    def set_privilege(self, privilege):
        assert isinstance(privilege, UserPrivilege)
        query = "UPDATE _user SET privilege = %s WHERE id = %s"
        database.query(query, privilege.value, self.id)

    def check_password(self, password):
        return bcrypt.checkpw(password.encode("utf-8"), self.password.encode("utf-8"))

    def as_json_data(self):
        return {
            "username": self.username,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "privilege": self.privilege.value,
            "password": self.password,
            "contests": [c.name for c in self.contests]
        }

