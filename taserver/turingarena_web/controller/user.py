from flask import session

from turingarena_web.model.contest import Contest
from turingarena_web.model.user import User


def get_current_user(contest):
    username = session.get(contest, None)
    if username is None:
        return None
    return User.from_username(Contest.contest(contest), username)


def set_current_user(contest, user):
    if user is None:
        session.clear()
    else:
        session[contest] = user.username
