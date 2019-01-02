from collections import namedtuple
from enum import Enum

import bcrypt
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
        query = "SELECT u.* FROM _user u JOIN user_contest uc on u.id = uc.user_id WHERE uc.contest_id = %s"
        return database.query_all(query, contest.id, convert=User)

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

    def set_privilege(self, privilege):
        assert isinstance(privilege, UserPrivilege)
        query = "UPDATE _user SET privilege = %s WHERE id = %s"
        database.query(query, privilege.value, self.id)

    def auth(self, password):
        return bcrypt.checkpw(password.encode("utf-8"), self.password.encode("utf-8"))
