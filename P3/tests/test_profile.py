from dances.db import get_db
from flask import Flask
from flask.testing import FlaskClient
from typing import Any

def test_view_profile(client: FlaskClient, auth: Any) -> None:
    auth.register()
    auth.login()
    response = client.get('/profile/')
    assert response.status_code == 200
    response_text = response.data.decode('utf-8')
    assert '<title>My Profile - Dance Collection</title>' in response_text
    assert 'testtestingauth' in response_text  # Username
    assert 'testname' in response_text  # Name
    assert 'test@test.com' in response_text  # Email

def test_update_profile_success(client: FlaskClient, auth: Any, app: Flask) -> None:
    auth.register()
    auth.login()
    response = client.post('/profile/update', data={
        'name': 'Updated Name',
        'email': 'updated@test.com',
        'state': 'Updated State',
        'city': 'Updated City'
    }, follow_redirects=True)
    assert response.status_code == 200
    response_text = response.data.decode('utf-8')
    assert 'Profile updated successfully!' in response_text
    with app.app_context():
        user = get_db().execute(
            "SELECT * FROM User WHERE Username = ?",
            ('testtestingauth',)
        ).fetchone()
        assert user['Name'] == 'Updated Name'
        assert user['Email'] == 'updated@test.com'
        assert user['State'] == 'Updated State'
        assert user['City'] == 'Updated City'

def test_update_profile_missing_name(client: FlaskClient, auth: Any) -> None:
    auth.register()
    auth.login()
    response = client.post('/profile/update', data={
        'name': '',
        'email': 'updated@test.com',
        'state': 'Updated State',
        'city': 'Updated City'
    }, follow_redirects=True)
    assert response.status_code == 200
    response_text = response.data.decode('utf-8')
    assert 'Name is required.' in response_text

def test_update_profile_invalid_email(client: FlaskClient, auth: Any) -> None:
    auth.register()
    auth.login()
    response = client.post('/profile/update', data={
        'name': 'Updated Name',
        'email': 'invalid-email',
        'state': 'Updated State',
        'city': 'Updated City'
    }, follow_redirects=True)
    assert response.status_code == 200
    response_text = response.data.decode('utf-8')
    assert 'Invalid email address.' in response_text