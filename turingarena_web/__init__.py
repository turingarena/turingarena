import logging
import sys

from flask import Flask

from turingarena_web.views.user import user
from turingarena_web.views.root import root_bp
from turingarena_web.views.problem import problem_bp
from turingarena_web.views.submission import submission_bp
from turingarena_web.views.admin import admin_bp
from turingarena_web.views.contest import contest_bp
from .config import config


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
    app.config.from_mapping(config)
    app.register_blueprint(root_bp, url_prefix="/")
    app.register_blueprint(user, url_prefix="/user")
    app.register_blueprint(problem_bp, url_prefix="/problem")
    app.register_blueprint(submission_bp, url_prefix="/submission")
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(contest_bp, url_prefix="/contest")

    init_logger(app, app.config.get("LOG_LEVEL", "INFO"))
    return app


if __name__ == "__main__":
    create_app().run()
