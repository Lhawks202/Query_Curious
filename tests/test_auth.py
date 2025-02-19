import pytest
from flask import g, session, Blueprint
from northwind.db import get_db
from northwind.auth import login_required

def test_register(client, app, auth):
    # Test GET request to register page
    assert client.get('/auth/register').status_code == 200

    response = auth.register(username='', password='test')
    response_text = response.data.decode('utf-8')
    assert 'User ID is required.' in response_text

    response = auth.register(username='', password='')
    response_text = response.data.decode('utf-8')
    assert 'User ID is required.' in response_text

    response = auth.register(username='test', password='')
    response_text = response.data.decode('utf-8')
    assert 'Password is required.' in response_text

    # Test POST request to register a new user
    response = auth.register()
    assert response.headers['Location'] == '/auth/login'

    # Check if the user was added to the database
    with app.app_context():
        assert get_db().execute(
            "SELECT * FROM Authentication WHERE UserID = 'test'",
        ).fetchone() is not None

def test_register_existing_user(client, app, auth ):
    response = auth.register()
    response = auth.register()
    response_text = response.data.decode('utf-8')
    assert 'Customer already exists—try logging in!' in response_text

def test_login(client, auth):
    # Test GET request to login page
    assert client.get('/auth/login').status_code == 200

    # Register a new user
    response = auth.register()
    
    response = auth.login(username='invalid', password='test')
    assert b'Incorrect user id.' in response.data

    response = auth.login(username='test', password='invalid')
    assert b'Incorrect password.' in response.data

    # Test POST request to login with valid credentials
    response = auth.login()
    assert response.headers['Location'] == '/', 'Redirect location is incorrect.'

    # Check if the user_id is stored in the session
    with client:
        client.get('/')
        assert session['user_id'] == 'test'

    # Test POST request to login with invalid credentials

def test_logout(client, auth):
    auth.login()

    with client:
        auth.logout()
        assert 'user_id' not in session

def test_load_logged_in_user(client, auth, app):
    # Register and login a new user
    client.post('/auth/register', data={'user_id': 'test', 'password': 'test'})
    auth.login()

    with client:
        client.get('/')
        assert g.user['UserID'] == 'test'

def test_login_required(client, auth, app):
    # Create a temporary blueprint for testing
    test_bp = Blueprint('test_bp', __name__)

    @test_bp.route('/protected')
    @login_required
    def protected():
        return 'Protected'
    app.register_blueprint(test_bp)

    # Register and login a new user
    auth.register()

    response = client.get('/protected')
    assert response.headers['Location'] == '/auth/login'

    # Test accessing the protected route after logging in
    auth.login()
    response = client.get('/protected')
    assert response.status_code == 200
    assert b'Protected' in response.data