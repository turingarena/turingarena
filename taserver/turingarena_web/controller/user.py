from flask import Blueprint, render_template, redirect, url_for, session

from turingarena_web.model.user import User


user_bp = Blueprint("user", __name__)


@user_bp.route("/login")
def login():
    return render_template("login.html")


@user_bp.route("/logout")
def logout():
    set_current_user(None)
    return redirect(url_for("main.home"))


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
