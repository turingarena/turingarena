from flask import render_template
from turingarena_web.user import UserPrivilege
from turingarena_web.views.user import get_current_user


def is_admin():
    return get_current_user() is not None and get_current_user().privilege == UserPrivilege.ADMIN


def render_template_ex(template, **kwargs):
    return render_template(template, user=get_current_user(), **kwargs)
