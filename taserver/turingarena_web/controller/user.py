from flask import Blueprint, request, render_template, redirect, url_for, abort, session

from turingarena_web.config import config
from turingarena_web.model.user import User


user_bp = Blueprint("user", __name__)


@user_bp.route("/login")
def login():
    reg_ok = config.get("allow_registration", False)
    return render_template("login.html", registrarion_allowed=reg_ok)


@user_bp.route("/logout")
def logout():
    set_current_user(None)
    return redirect(url_for("main.home"))


@user_bp.route("/register", methods=("GET", "POST"))
def register():
    if not config.get("allow_registration", False):
        return abort(403)
    if request.method == "GET":
        return render_template("register.html")

    user = User.insert(
        username=request.form["username"],
        first_name=request.form["first_name"],
        last_name=request.form["last_name"],
        email=request.form["email"],
        password=request.form["password"],
    )

    set_current_user(user)

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
