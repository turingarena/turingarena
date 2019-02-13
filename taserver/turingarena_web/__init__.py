from flask import Flask

from turingarena_web.controller.user import user_bp
from turingarena_web.controller.root import root_bp
from turingarena_web.controller.submission import submission_bp
from turingarena_web.controller.contest import contest_bp
from turingarena_web.config import config
from turingarena_web.init_logger import init_logger


def create_app():
    app = Flask(__name__)
    app.config.from_mapping(config.__dict__)
    app.register_blueprint(root_bp, url_prefix="/")
    app.register_blueprint(user_bp, url_prefix="/user")
    app.register_blueprint(submission_bp, url_prefix="/submission")
    app.register_blueprint(contest_bp, url_prefix="/")

    init_logger()

    return app
