import re

from flask import Blueprint, request, render_template, session, redirect, url_for

from turingarena_web.database import UserDatabase

user = Blueprint("user", __name__)
user_db = UserDatabase()


@user.route("/")
def user_():
    if "username" in session:
        return redirect(url_for("user.user_view", username=session["username"]))
    return redirect("user.login")


@user.route("/<username>")
def user_view(username):
    return render_template("user.html", user=user_db.get_by_username(username))


@user.route("/login", methods=("GET", "POST"))
def login():
    if request.method == "GET":
        return render_template("login.html")
    username = request.form["username"]
    password = request.form["password"]

    if user_db.authenticate(username, password):
        session["username"] = username
        return redirect(url_for("user.user_view", username=username))
    else:
        return render_template("login.html", message="Wrong username or password")


@user.route("/logout")
def logout():
    if "username" in session:
        del session["username"]
    redirect(url_for("/"))


@user.route("/register", methods=("GET", "POST"))
def register():
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

    assert user_db.insert(
        username=username,
        first_name=first_name,
        last_name=last_name,
        email=email,
        password=password,
    )

    session["username"] = username

    return redirect(url_for("user"))

