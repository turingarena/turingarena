from flask import Flask
from turingarena_web.controller.api import api

from turingarena_web.controller.user import user_bp
from turingarena_web.controller.root import root
from turingarena_web.config import config
from turingarena_web.logging import init_logger


def create_app():
    app = Flask(__name__)
    app.config.from_mapping(config.__dict__)
    app.register_blueprint(root, url_prefix="/")
    app.register_blueprint(user_bp, url_prefix="/")
    app.register_blueprint(api, url_prefix="/api")

    init_logger()

    return app
