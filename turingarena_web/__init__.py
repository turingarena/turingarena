from flask import Flask

from .user import user
from .root import root
from .problem import problem_bp
from .submission import submission


def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('config.py')
    app.register_blueprint(root, url_prefix='/')
    app.register_blueprint(user, url_prefix='/user')
    app.register_blueprint(problem_bp, url_prefix='/problem')
    app.register_blueprint(submission, url_prefix='/submission')
    return app


if __name__ == '__main__':
    create_app().run()
