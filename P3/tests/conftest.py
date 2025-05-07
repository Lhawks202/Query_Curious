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
                "INSERT INTO Steps (DanceID, StepName) VALUES (?, ?)",
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
                "INSERT INTO FigureStep (StepsId, FigureId, Place) VALUES (?, ?, ?)",
                (step_id, figure_id, place)
            )
            db.commit()
            return cursor.lastrowid

    '''def insert_learning(self, user_id: str = 'testtestingauth', dance_id: int = 1, date_added: str = '2025-05-01') -> int:
        with self._app.app_context():
            db = get_db()
            cursor = db.execute(
                "INSERT INTO Learning (UserId, DanceId, DateAdded) VALUES (?, ?, ?)",
                (user_id, dance_id, date_added)
            )
            db.commit()
            return cursor.lastrowid

    def insert_favorites(self, user_id: str = 'testtestingauth', dance_id: int = 1, date_added: str = '2025-05-01') -> int:
        with self._app.app_context():
            db = get_db()
            cursor = db.execute(
                "INSERT INTO Favorites (UserId, DanceId, DateAdded) VALUES (?, ?, ?)",
                (user_id, dance_id, date_added)
            )
            db.commit()
            return cursor.lastrowid
    
    def testing_populate(self) -> None:
        with self._app.app_context():
            db = get_db()
            dance_ids = []
            for i in range(3):
                dance_id = self.insert_dance(
                    dance_name=f'Dance {i}',
                    video=f'dance{i}.mp4',
                    source=f'Source {i}'
                )
                dance_ids.append(dance_id)
            step_ids = []
            for i, dance_id in enumerate(dance_ids, start=1):
                for j in range(2):  # 2 steps per dance
                    step_id = self.insert_step(
                        dance_id=dance_id,
                        step_name=f'Step {i}-{j}'
                    )
                    step_ids.append(step_id)
            figure_ids = []
            for i in range(3):
                figure_id = self.insert_figure(
                    name=f'Figure {i}',
                    roles='Lead, Follow',
                    start_position='Closed',
                    action=f'Action {i}',
                    end_position='Open',
                    duration= i
                )
                figure_ids.append(figure_id)
            for i, figure_id in enumerate(figure_ids):
                # Each figure gets 2 steps
                self.insert_figure_step(step_id=step_ids[i * 2], figure_id=figure_id, place=1)
                self.insert_figure_step(step_id=step_ids[i * 2 + 1], figure_id=figure_id, place=2)
            db.commit()
            return dance_ids'''


@pytest.fixture(scope='function')
def auth(client: FlaskClient) -> AuthActions:
    return AuthActions(client)

@pytest.fixture(scope='function')
def insert(client: FlaskClient, app: Flask) -> InsertActions:
    return InsertActions(client, app)
