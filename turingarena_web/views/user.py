import re

from flask import Blueprint, request, render_template, session, redirect, url_for, current_app, abort

from turingarena_web.user import User

user = Blueprint("user", __name__)


def get_current_user():
    if "username" not in session:
        return None
    return User.from_username(session["username"])


@user.route("/")
def user_():
    if "username" in session:
        return redirect(url_for("user.user_view", username=session["username"]))
    return redirect(url_for("user.login"))


@user.route("/<username>")
def user_view(username):
    return render_template("user.html", user=User.from_username(username))


@user.route("/login", methods=("GET", "POST"))
def login():
    reg_ok = current_app.config.get("REGISTRATION_ALLOWED", True)
    redirect_url = request.args.get("redirect", None)
    if request.method == "GET":
        return render_template("login.html", registrarion_allowed=reg_ok, redirect=redirect_url)
    username = request.form["username"]
    password = request.form["password"]

    user = User.from_username(username)
    if user.auth(password):
        session["username"] = username
        if redirect_url is None:
            redirect_url = url_for("user.user_view", username=username)
        return redirect(redirect_url)
    else:
        return render_template("login.html", redirect=redirect_url, message="Wrong username or password",
                               registrarion_allowed=reg_ok)


@user.route("/logout")
def logout():
    if "username" in session:
        del session["username"]
    return redirect(url_for("root.home"))


@user.route("/register", methods=("GET", "POST"))
def register():
    if "ALLOW_REGISTRATION" not in current_app.config or not current_app.config["ALLOW_REGISTRATION"]:
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

    assert User.insert(
        username=username,
        first_name=first_name,
        last_name=last_name,
        email=email,
        password=password,
    )

    session["username"] = username

    return redirect(url_for("user_view"))
