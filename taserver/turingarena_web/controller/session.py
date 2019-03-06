from flask import session
from turingarena_web.model.user import User


def get_current_user():
    username = session.get("username", None)
    if username is None:
        return None
    return User.from_username(username)


def set_current_user(user):
    if user is None:
        session.clear()
    else:
        session["username"] = user.username

