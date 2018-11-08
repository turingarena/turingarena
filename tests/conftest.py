import pytest

from turingarena_web import create_app


@pytest.fixture
def app():
    app = create_app()
    return app
