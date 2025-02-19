import shutil
import os
import pytest
import sys 
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from northwind import create_app, db
TEST_DB = "test_northwind.sqlite"

@pytest.fixture(scope='function')
def app():
    shutil.copyfile('./northwind/northwind.sqlite', TEST_DB)

    app = create_app()
    app.config['DATABASE'] = TEST_DB

    with app.app_context():
        db.init_db()
        yield app
    os.remove(TEST_DB)

@pytest.fixture(scope='function')
def client(app):
    return app.test_client()

@pytest.fixture(scope='function')
def runner(app):
    return app.test_cli_runner()

class AuthActions(object):
    def __init__(self, client):
        self._client = client

    def register(self, username='test', password='test'):
        return self._client.post(
            '/auth/register',
            data={'user_id': username, 'password': password}
        )

    def login(self, username='test', password='test'):
        return self._client.post(
            '/auth/login',
            data={'user_id': username, 'password': password}
        )

    def logout(self):
        return self._client.get('/auth/logout')


@pytest.fixture
def auth(client):
    return AuthActions(client)