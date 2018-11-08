from flask import Blueprint, render_template

root = Blueprint('root', __name__)


@root.route('/')
def home():
    return render_template('home.html')
