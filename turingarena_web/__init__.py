import logging
import sys

from flask import Flask

from .user import user
from .root import root_bp
from .problem import problem_bp
from .submission import submission
from .admin import admin_bp


def init_logger(app, level):
    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(level)
    handler.setFormatter(logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s: %(message)s"
    ))
    logging.getLogger().addHandler(handler)
    logging.getLogger().setLevel(level)
    app.logger.handlers = []
    app.logger.propagate = True


def create_app():
    app = Flask(__name__)
    if app.debug:
        app.config.from_pyfile("config.py")
    else:
        app.config.from_pyfile("/etc/turingarnea.conf")
    app.register_blueprint(root_bp, url_prefix="/")
    app.register_blueprint(user, url_prefix="/user")
    app.register_blueprint(problem_bp, url_prefix="/problem")
    app.register_blueprint(submission, url_prefix="/submission")
    app.register_blueprint(admin_bp, url_prefix="/admin")

    init_logger(app, app.config.get("LOG_LEVEL", "INFO"))
    return app


if __name__ == "__main__":
    create_app().run()
