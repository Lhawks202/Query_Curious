import shutil
import os
import pytest
import sys 
from flask import session, Flask, g
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
    @app.teardown_appcontext
    def close_db_connection(exception):
        db = g.pop('db', None)
        if db is not None:
            db.close()
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

    def register(self, username: str = 'testtestingauth', password: str = 'testtestingauth', name = 'testname', email = 'test@test.com', next: str = '/') -> 'Response':
        return self._client.post(
            'auth/register',
            data={'user_id': username, 'password': password, 'name': name, 'email': email, 'state': '', 'city': '', 'next': next}
        )

    def login(self, username: str = 'testtestingauth', password: str = 'testtestingauth', next: str = '/') -> 'Response':
        return self._client.post(
            'auth/login',
            data={'user_id': username, 'password': password, 'next': next}
        )

    def logout(self) -> 'Response':
        return self._client.get('auth/logout')

class InsertActions(object):
    def __init__(self, client: FlaskClient, app: Flask) -> None:
        self._client = client
        self._app = app

    def insert_dance(self, dance_name: str = 'testdance', video: str = 'testvideo', source: str = 'testsource') -> int:
        with self._app.app_context():
            db = get_db()
            cursor = db.execute(
                "INSERT INTO Dance (DanceName, Video, Source) VALUES (?, ?, ?)",
                (dance_name, video, source)
            )
            db.commit()
            return cursor.lastrowid

    def insert_step(self, dance_id: int = 1, step_name: str = 'teststep') -> int:
        with self._app.app_context():
            db = get_db()
            cursor = db.execute(
                "INSERT INTO Step (DanceID, StepName) VALUES (?, ?)",
                (dance_id, step_name)
            )
            db.commit()
            return cursor.lastrowid

    def insert_figure(self, name: str = 'testfigure', roles: str = 'Lead, Follow',
                      start_position: str = 'Closed', action: str = 'Turn', end_position: str = 'Open',
                      duration: int = 5) -> int:
        with self._app.app_context():
            db = get_db()
            cursor = db.execute(
                "INSERT INTO Figure (Name, Roles, StartPosition, Action, EndPosition, Duration) VALUES (?, ?, ?, ?, ?, ?)",
                (name, roles, start_position, action, end_position, duration)
            )
            db.commit()
            return cursor.lastrowid

    def insert_figure_step(self, step_id: int = 1, figure_id: int = 1, place: int = 1) -> int:
        with self._app.app_context():
            db = get_db()
            cursor = db.execute(
                "INSERT INTO FigureStep (StepId, FigureId, Place) VALUES (?, ?, ?)",
                (step_id, figure_id, place)
            )
            db.commit()
            return cursor.lastrowid

@pytest.fixture(scope='function')
def auth(client: FlaskClient) -> AuthActions:
    return AuthActions(client)

@pytest.fixture(scope='function')
def insert(client: FlaskClient, app: Flask) -> InsertActions:
    return InsertActions(client, app)
