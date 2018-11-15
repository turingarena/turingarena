from flask import session

from turingarena_web.model.contest import Contest
from turingarena_web.model.user import User


def get_current_user():
    user_id = session.get("current_user")
    if user_id is None:
        return None
    return User.from_id(user_id)


def set_current_user(user):
    if user is None:
        del session["current_user"]
    else:
        session["current_user"] = user.id


def get_current_contest():
    contest_id = session.get("current_contest")
    if contest_id is None:
        return None
    return Contest.from_id(contest_id)


def set_current_contest(contest):
    if contest is None:
        del session["current_contest"]
    else:
        session["current_contest"] = contest.id
