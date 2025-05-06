import pytest
from flask import g
from dances.db import get_db

def test_learning_not_logged_in(client):
    response = client.get('/learning/')
    assert response.status_code == 200
    response_text = response.data.decode('utf-8')
    assert '<h1>Error: not logged in</h1>' in response_text

def test_learning_with_no_dances(client, app, auth):
    with app.app_context():
        auth.register()
        auth.login()
    response = client.get('/learning/')
    assert response.status_code == 200
    response_text = response.data.decode('utf-8')
    assert 'No learning dances found' in response_text

def test_learning_with_dances(client, app, auth, insert):
    with app.app_context():
        auth.register()
        auth.login()
        dance_ids = insert.testing_populate()
        for id in dance_ids:
            insert.insert_learning(id)
        response = client.get('/learning/')
        assert response.status_code == 200
        response_text = response.data.decode('utf-8')
        print(response_text)
        for i in range(len(dance_ids)):
            assert f"Dance {i}" in response_text
