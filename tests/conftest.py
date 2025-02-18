import shutil
import os
import pytest
from northwind import create_app, db
TEST_DB = "test_northwind.sqlite"

@pytest.fixture(scope='session')
def app():
    shutil.copyfile('../northwind/northwind.sqlite', TEST_DB)

    app = create_app()
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{TEST_DB}'

    with app.app_context():
        db.create_all()
        yield app
    os.remove(TEST_DB)

@pytest.fixture(scope='session')
def client(app):
    return app.test_client()

@pytest.fixture(scope='session')
def runner(app):
    return app.test_cli_runner()

class AuthActions(object):
    def __init__(self, client):
        self._client = client

    def login(self, username='test', password='test'):
        return self._client.post(
            '/auth/login',
            data={'username': username, 'password': password}
        )

    def logout(self):
        return self._client.get('/auth/logout')


@pytest.fixture
def auth(client):
    return AuthActions(client)