import re

from flask import Blueprint, request, render_template, redirect, url_for, abort

from turingarena_web.model.contest import Contest
from turingarena_web.model.user import User, UserPrivilege
from turingarena_web.config import config
from turingarena_web.controller import session

user_bp = Blueprint("user", __name__)


@user_bp.route("/")
def user_():
    user = session.get_current_user()
    if user is not None:
        return redirect(url_for("user.user_view", username=user.username))
    return redirect(url_for("user.login"))


@user_bp.route("/<username>")
def user_view(username):
    user = User.from_username(username)

    if user.privilege == UserPrivilege.STANDARD and user != session.get_current_user():
        return abort(403)

    contests = Contest.of_user(user)
    return render_template("user.html", user=user, contests=contests)


@user_bp.route("/login", methods=("GET", "POST"))
def login():
    reg_ok = config.get("allow_registration", False)
    redirect_url = request.args.get("redirect", None)
    if request.method == "GET":
        return render_template("login.html", registrarion_allowed=reg_ok, redirect=redirect_url)
    username = request.form["username"]
    password = request.form["password"]

    user = User.from_username(username)
    if user.auth(password):
        session.set_current_user(user)
        if redirect_url is None:
            redirect_url = url_for("user.user_view", username=username)
        return redirect(redirect_url)
    else:
        return render_template("login.html", redirect=redirect_url, message="Wrong username or password",
                               registrarion_allowed=reg_ok)


@user_bp.route("/logout")
def logout():
    session.set_current_user(None)
    return redirect(url_for("root.home"))


@user_bp.route("/register", methods=("GET", "POST"))
def register():
    if not config.get("allow_registration", False):
        return abort(403)
    if request.method == "GET":
        return render_template("register.html")

    # TODO: validate all data properly
    username = request.form["username"]
    assert len(username) > 0

    first_name = request.form["first_name"]
    assert len(first_name) > 0

    last_name = request.form["last_name"]
    assert len(last_name) > 0

    email = request.form["email"]
    assert re.match("[^@]+@[^@]+\.[^@]+", email)

    password = request.form["password"]
    password2 = request.form["password2"]

    assert len(password) > 4 and password == password2

    user = User.insert(
        username=username,
        first_name=first_name,
        last_name=last_name,
        email=email,
        password=password,
    )

    session.set_current_user(user)

    return redirect(url_for("user_view"))
