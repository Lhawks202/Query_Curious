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

def test_learning_with_dances(client, app, auth, insert):
    with app.app_context():
        auth.register()
        auth.login()
        dance_ids = []
        for i in range(3):
            dance_id = insert.insert_dance(dance_name=f'Dance {i}', video=f'dance{i}.mp4', source=f'Source {i}')
            dance_ids.append(dance_id)
            response = client.post('/learning', json={
                'danceId': dance_id,
                'date': '2025-05-01'
            })
        response = client.get('/learning')
        assert response.status_code == 200
        response_text = response.data.decode('utf-8')
        for i in range(len(dance_ids)):
            assert f"Dance {i}" in response_text

def test_favorites_not_logged_in(client):
    response = client.get('/favorites', follow_redirects=False)
    assert response.status_code == 302
    assert response.headers['Location'] == '/auth/login'

def test_add_favorites(client, app, auth, insert):
    """Test adding a dance to the learning list via POST."""
    with app.app_context():
        auth.register()
        auth.login()
        dance_id = insert.insert_dance(dance_name='Test Dance', video='test.mp4', source='Test Source')
    response = client.post('/favorites', json={
        'danceId': dance_id,
        'date': '2025-05-01',
        'rating': 5
    })
    assert response.status_code == 200
    response_json = response.get_json()
    assert response_json['status'] == 'added'
    with app.app_context():
        favorites_entry = get_db().execute(
            "SELECT * FROM Favorites WHERE DanceId = ? AND UserId = ?",
            (dance_id, 'testtestingauth')
        ).fetchone()
        assert favorites_entry is not None
        assert favorites_entry['DateAdded'] == '2025-05-01'
        assert favorites_entry['Rating'] == 5

def test_favorites_with_dances(client, app, auth, insert):
    with app.app_context():
        auth.register()
        auth.login()
        dance_ids = []
        for i in range(3):
            dance_id = insert.insert_dance(dance_name=f'Dance {i}', video=f'dance{i}.mp4', source=f'Source {i}')
            dance_ids.append(dance_id)
            response = client.post('/favorites', json={
                'danceId': dance_id,
                'date': '2025-05-01',
                'rating': i
            })
        response = client.get('/favorites')
        assert response.status_code == 200
        response_text = response.data.decode('utf-8')
        for i in range(len(dance_ids)):
            assert f"Dance {i}" in response_text

