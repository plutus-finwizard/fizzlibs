import os
import tempfile

import pytest

from app import create_app

@pytest.fixture(scope='session')
def app():

    app = create_app({
        'TESTING': True
    })

    yield app


@pytest.fixture(scope='session')
def client(app):
    return app.test_client()


@pytest.fixture(scope='session')
def runner(app):
    return app.test_cli_runner()
