from dances.db import get_db
from flask import g, session, Flask
from flask.testing import FlaskClient
from typing import Any

def test_register(client: FlaskClient, app: Flask, auth: Any) -> None:
    client.get('/')
    assert client.get('/auth/register').status_code == 200, "Missing registration page."
    # Test invalid registration attempts
    response = auth.register(username='', password='testtestingauth')
    response_text = response.data.decode('utf-8')
    assert 'User ID is required.' in response_text
    response = auth.register(username='', password='')
    response_text = response.data.decode('utf-8')
    assert 'User ID is required.' in response_text
    response = auth.register(username='test', password='')
    response_text = response.data.decode('utf-8')
    assert 'Password is required.' in response_text
    # Test successful registration and redirection
    response = auth.register()
    # Check if the user was added to the database
    with app.app_context():
        assert get_db().execute(
            "SELECT * FROM User WHERE Username = ?", ('testtestingauth',)
        ).fetchone() is not None
    response = auth.register(username='testtestingauth2', password='testtestingauth2', next='/')
    # Check if the user was added to the database
    with app.app_context():
        assert get_db().execute(
            "SELECT * FROM User WHERE Username = 'testtestingauth2'",
        ).fetchone() is not None
    assert response.headers['Location'] == '/', "Post registration redirect location is incorrect."

def test_register_existing_user(client: FlaskClient, auth: Any) -> None:
    auth.register()
    response = auth.register()
    response_text = response.data.decode('utf-8')
    print(response_text)
    with client.session_transaction() as sess:
        print(sess.get('_flashes', []))
    assert 'User already exists—try logging in!' in response_text
    
def test_register_strange_characters(auth: Any) -> None:
    response = auth.register(username='test_!@#$%^*&()`\'', password='test_!@#$%^*&()`\'')
    assert response.headers['Location'] == '/',  "Doesn't accept strange characters in username and password."
    response = auth.register(username='éñçøßΩ中あ😊€', password='éñçøßΩ中あ😊€')
    assert response.headers['Location'] == '/',  "Doesn't accept strange characters in username and password."

def test_sql_injection_drop_table_register(app: Flask, auth: Any) -> None:
    with app.app_context():
        # Attempt to register with SQL injection in the user_id to drop the User table
        response = auth.register(username="'; DROP TABLE User; --", password='password')
        assert response.status_code == 302

        # Verify that the Customer table still exists
        db = get_db()
        try:
            db.execute('SELECT 1 FROM User LIMIT 1')
        except Exception as e:
            assert False, f"Customer table was dropped: {e}"

def test_login(client: FlaskClient, auth: Any) -> None:
    auth.register()
    # Test invalid login attempts
    response = auth.login(username='invalid', password='testtestingauth')
    assert b'Incorrect user id.' in response.data
    response = auth.login(username='testtestingauth', password='invalid')
    assert b'Incorrect password.' in response.data
    # Test successful login and redirection
    response = auth.login()

    assert response.headers['Location'] == '/', "Post login redirect location is incorrect."
    with client:
        assert client.get('/').status_code == 200, "Internal Server Error on Login"
        assert session['user_id'] == 'testtestingauth'

def test_sql_injection_drop_table_login(app: Flask, auth: Any) -> None:
    with app.app_context():
        auth.register()
        # Attempt to login with SQL injection in the user_id to drop the Authentication table
        response = auth.login(username="'; DROP TABLE User; --", password='password')
        assert response.status_code == 200
        response_text = response.data.decode('utf-8')
        assert 'Incorrect user id.' in response_text
        db = get_db()
        try:
            db.execute('SELECT 1 FROM User LIMIT 1')
        except Exception as e:
            assert False, f"User table was dropped: {e}"

def test_logout(client: FlaskClient, auth: Any) -> None:
    auth.register()
    auth.login()
    with client:
        client.get('/')
        assert session['user_id'] == 'testtestingauth'
        auth.logout()
        assert 'test' not in session

def test_load_logged_in_user(client: FlaskClient, auth: Any) -> None:
    auth.register()
    auth.login()
    with client:
        client.get('/')
        assert g.user['Username'] == 'testtestingauth'