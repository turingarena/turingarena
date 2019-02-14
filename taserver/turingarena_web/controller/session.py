import secrets

from collections import namedtuple
from flask import session

from turingarena_web.model.user import User
from turingarena_web.model.database import database


class Session(namedtuple("Session", ["cookie", "user_id", "timestamp"])):
    @staticmethod
    def current_session():
        cookie = session.get("cookie")
        if cookie is None:
            return None
        query = "SELECT * FROM session WHERE cookie = %s"
        return database.query_one(query, cookie, convert=Session)

    @staticmethod
    def new_session(user):
        session["cookie"] = secrets.token_hex(32)
        query = "INSERT INTO session(cookie, user_id) VALUES (%s, %s) RETURNING *"
        return database.query_one(query, session["cookie"], user.id, convert=Session)

    @property
    def user(self):
        return User.from_id(self.user_id)

    def delete(self):
        query = "DELETE FROM session WHERE cookie = %s"
        database.query(query, self.cookie)


def get_current_user():
    current_session = Session.current_session()
    if current_session is None:
        return None
    return Session.current_session().user


def set_current_user(user):
    current_session = Session.current_session()
    if current_session is not None:
        current_session.delete()
    if user is not None:
        Session.new_session(user)

