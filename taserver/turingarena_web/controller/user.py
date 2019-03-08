from flask import Blueprint, request, render_template, redirect, url_for, abort

from turingarena_web.config import config
from turingarena_web.controller import session
from turingarena_web.model.user import User


user_bp = Blueprint("user", __name__)


@user_bp.route("/login", methods=("GET", "POST"))
def login():
    reg_ok = config.get("allow_registration", False)
    if request.method == "GET":
        return render_template("login.html", registrarion_allowed=reg_ok)

    user = User.from_username(request.form["username"])

    if user is None or not user.check_password(request.form["password"]):
        return render_template("login.html", message="Wrong username or password", registrarion_allowed=reg_ok)
    else:
        session.set_current_user(user)
        return redirect(url_for("root.home"))


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

    user = User.insert(
        username=request.form["username"],
        first_name=request.form["first_name"],
        last_name=request.form["last_name"],
        email=request.form["email"],
        password=request.form["password"],
    )

    session.set_current_user(user)

    return redirect(url_for("root.home"))
