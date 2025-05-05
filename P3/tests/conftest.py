import shutil
import os
import pytest
import sys 
from flask import session, Flask
from flask.testing import FlaskClient
from flask_wtf.csrf import generate_csrf
from typing import Optional
from click.testing import CliRunner

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dances import create_app, db
from dances.db import get_db

TEST_DB = "./tests/test_dances.sqlite"

@pytest.fixture(scope='function')
def app():
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)
    app = create_app()
    app.config['DATABASE'] = TEST_DB
    app.config['WTF_CSRF_ENABLED'] = False
    with app.app_context():
        db.init_db()
        runner = CliRunner()
        result = runner.invoke(app.cli.commands['init-db'], ['--populate'], catch_exceptions=False)
        assert result.exit_code == 0
    return app

@pytest.fixture(scope='function')
def client(app: Flask) -> FlaskClient:
    return app.test_client()

@pytest.fixture(scope='function')
def runner(app: Flask) -> 'FlaskCliRunner':
    return app.test_cli_runner()

class AuthActions(object):
    def __init__(self, client: FlaskClient) -> None:
        self._client = client

    def register(self, username: str = 'testtestingauth', password: str = 'testtestingauth', next: str = '/') -> 'Response':
        return self._client.post(
            'auth/register',
            data={'user_id': username, 'password': password, 'next': next}
        )

    def login(self, username: str = 'testtestingauth', password: str = 'testtestingauth', next: str = '/') -> 'Response':
        return self._client.post(
            'auth/login',
            data={'user_id': username, 'password': password, 'next': next}
        )

    def logout(self) -> 'Response':
        return self._client.get('auth/logout')

@pytest.fixture(scope='function')
def auth(client: FlaskClient) -> AuthActions:
    return AuthActions(client)