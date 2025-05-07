import pytest
from flask import g
from dances.db import get_db

def test_learning_not_logged_in(client):
    response = client.get('/learning', follow_redirects=False)
    assert response.status_code == 302
    assert response.headers['Location'] == '/auth/login'

def test_learning_with_no_dances(client, app, auth):
    with app.app_context():
        auth.register()
        auth.login()
    response = client.get('/learning')
    assert response.status_code == 200
    response_text = response.data.decode('utf-8')
    assert 'No learning dances found' in response_text

def test_add_learning(client, app, auth, insert):
    """Test adding a dance to the learning list via POST."""
    with app.app_context():
        auth.register()
        auth.login()
        dance_id = insert.insert_dance(dance_name='Test Dance', video='test.mp4', source='Test Source')
    response = client.post('/learning', json={
        'action': 'add',
        'danceId': dance_id,
        'date': '2025-05-01'
    })
    assert response.status_code == 200
    response_json = response.get_json()
    assert response_json['status'] == 'added'
    with app.app_context():
        learning_entry = get_db().execute(
            "SELECT * FROM Learning WHERE DanceId = ? AND UserId = ?",
            (dance_id, 'testtestingauth')
        ).fetchone()
        assert learning_entry is not None
        assert learning_entry['DateAdded'] == '2025-05-01'

def test_learned_not_logged_in(client):
    response = client.get('/learned', follow_redirects=False)
    assert response.status_code == 302
    assert response.headers['Location'] == '/auth/login'

def test_add_learned(client, app, auth, insert):
    """Test adding a dance to the learning list via POST."""
    with app.app_context():
        auth.register()
        auth.login()
        dance_id = insert.insert_dance(dance_name='Test Dance', video='test.mp4', source='Test Source')
    response = client.post('/learned', json={
        'action': 'add',
        'danceId': dance_id,
        'date': '2025-05-01',
        'rating': 5
    })
    assert response.status_code == 200
    response_json = response.get_json()
    assert response_json['status'] == 'added'
    with app.app_context():
        learned_entry = get_db().execute(
            "SELECT * FROM Learned WHERE DanceId = ? AND UserId = ?",
            (dance_id, 'testtestingauth')
        ).fetchone()
        assert learned_entry is not None
        assert learned_entry['DateAdded'] == '2025-05-01'
        assert learned_entry['Rating'] == 5

