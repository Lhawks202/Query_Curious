from dances.db import get_db
from flask import Flask
from flask.testing import FlaskClient
from typing import Any

def test_learning_not_logged_in(client: FlaskClient) -> None:
    response = client.get('/learning', follow_redirects=False)
    assert response.status_code == 302
    assert response.headers['Location'] == '/auth/login'

def test_add_learning(client: FlaskClient, app: Flask, auth: Any, insert: Any) -> None:
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

def test_remove_learning(client: FlaskClient, app: Flask, auth: Any, insert: Any) -> None:
    with app.app_context():
        auth.register()
        auth.login()
        dance_id = insert.insert_dance(dance_name='Test Dance', video='test.mp4', source='Test Source')
        get_db().execute(
            "INSERT INTO Learning (UserId, DanceId, DateAdded) VALUES (?, ?, ?)",
            ('testtestingauth', dance_id, '2025-05-01')
        )
        get_db().commit()
    response = client.post('/learning', json={
        'action': 'remove',
        'danceId': dance_id
    })
    assert response.status_code == 200
    response_json = response.get_json()
    assert response_json['status'] == 'removed'
    with app.app_context():
        learned_entry = get_db().execute(
            "SELECT * FROM Learning WHERE DanceId = ? AND UserId = ?",
            (dance_id, 'testtestingauth')
        ).fetchone()
        assert learned_entry is None

def test_learning_with_no_dances(client: FlaskClient, app: Flask, auth: Any) -> None:
    with app.app_context():
        auth.register()
        auth.login()
    response = client.get('/learning')
    assert response.status_code == 200
    response_text = response.data.decode('utf-8')
    assert 'No learning dances found' in response_text

def test_learning_with_empty_dances(client: FlaskClient, app: Flask, auth: Any, insert: Any, capsys: Any) -> None:
    with app.app_context():
        auth.register()
        auth.login()
        db = get_db()
        dance_ids = []
        for i in range(3):
            dance_id = insert.insert_dance(dance_name=f'Dance {i}', video=f'dance{i}.mp4', source=f'Source {i}')
            dance_ids.append(dance_id)
            response = client.post('/learning', json={
                'action': 'add',
                'danceId': dance_id,
                'date': f'2025-05-0{i + 1}',
            })
            db.commit()
        response = client.get('/learning')
        assert response.status_code == 200
        captured = capsys.readouterr()
        stdout_output = captured.out
        for i, dance_id in enumerate(dance_ids):
            assert f"Warning: no steps/figures associated with dance Dance {i} (id: {dance_id})" in stdout_output

def test_learning_with_dances(client: FlaskClient, app: Flask, auth: Any, insert: Any) -> None:
    with app.app_context():
        auth.register()
        auth.login()
        db = get_db()
        dance_ids = []
        for i in range(3):
            dance_id = insert.insert_dance(dance_name=f'Dance {i}', video=f'dance{i}.mp4', source=f'Source {i}')
            dance_ids.append(dance_id)
            step_id = insert.insert_step(dance_id=dance_id, step_name=f'Step {i}')
            figure_id = insert.insert_figure(
                name=f'Figure {i}',
                roles='Lead, Follow',
                start_position='Closed',
                action='Turn',
                end_position='Open',
                duration=5
            )
            insert.insert_figure_step(step_id=step_id, figure_id=figure_id, place=1)
            response = client.post('/learning', json={
                'action': 'add',
                'danceId': dance_id,
                'date': f'2025-05-0{i + 1}',
            })
            db.commit()
        response = client.get('/learning')
        assert response.status_code == 200
        response_text = response.data.decode('utf-8')
        print(response_text)
        for i in range(3):
            assert f"Dance {i}" in response_text
            assert f"Date started learning: 2025-05-0{i + 1}" in response_text

def test_learned_not_logged_in(client: FlaskClient) -> None:
    response = client.get('/learned', follow_redirects=False)
    assert response.status_code == 302
    assert response.headers['Location'] == '/auth/login'

def test_add_learned(client: FlaskClient, app: Flask, auth: Any, insert: Any) -> None:
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

def test_remove_learned(client: FlaskClient, app: Flask, auth: Any, insert: Any) -> None:
    with app.app_context():
        auth.register()
        auth.login()
        dance_id = insert.insert_dance(dance_name='Test Dance', video='test.mp4', source='Test Source')
        get_db().execute(
            "INSERT INTO Learned (UserId, DanceId, DateAdded, Rating) VALUES (?, ?, ?, ?)",
            ('testtestingauth', dance_id, '2025-05-01', 5)
        )
        get_db().commit()
    response = client.post('/learned', json={
        'action': 'remove',
        'danceId': dance_id
    })
    assert response.status_code == 200
    response_json = response.get_json()
    assert response_json['status'] == 'removed'
    with app.app_context():
        learned_entry = get_db().execute(
            "SELECT * FROM Learned WHERE DanceId = ? AND UserId = ?",
            (dance_id, 'testtestingauth')
        ).fetchone()
        assert learned_entry is None

def test_learned_no_dances(client: FlaskClient, app: Flask, auth: Any) -> None:
    with app.app_context():
        auth.register()
        auth.login()
        response = client.get('/learned')
        assert response.status_code == 200
        response_text = response.data.decode('utf-8')
        assert '<p>No learned dances found for this user. Go to home, choose a dance, and start learning!</p>' in response_text

def test_learned_with_empty_dances(client: FlaskClient, app: Flask, auth: Any, insert: Any, capsys: Any) -> None:
    with app.app_context():
        auth.register()
        auth.login()
        db = get_db()
        dance_ids = []
        for i in range(3):
            dance_id = insert.insert_dance(dance_name=f'Dance {i}', video=f'dance{i}.mp4', source=f'Source {i}')
            dance_ids.append(dance_id)
            response = client.post('/learned', json={
                'action': 'add',
                'danceId': dance_id,
                'date': f'2025-05-0{i + 1}',
                'rating': (i + 1)
            })
            db.commit()
        response = client.get('/learned')
        assert response.status_code == 200
        captured = capsys.readouterr()
        stdout_output = captured.out
        for i, dance_id in enumerate(dance_ids):
            assert f"Warning: no steps/figures associated with dance Dance {i} (id: {dance_id})" in stdout_output

def test_learned_with_dances(client: FlaskClient, app: Flask, auth: Any, insert: Any) -> None:
    with app.app_context():
        auth.register()
        auth.login()
        db = get_db()
        dance_ids = []
        for i in range(3):
            dance_id = insert.insert_dance(dance_name=f'Dance {i}', video=f'dance{i}.mp4', source=f'Source {i}')
            dance_ids.append(dance_id)
            step_id = insert.insert_step(dance_id=dance_id, step_name=f'Step {i}')
            figure_id = insert.insert_figure(
                name=f'Figure {i}',
                roles='Lead, Follow',
                start_position='Closed',
                action='Turn',
                end_position='Open',
                duration=5
            )
            insert.insert_figure_step(step_id=step_id, figure_id=figure_id, place=1)
            response = client.post('/learned', json={
                'action': 'add',
                'danceId': dance_id,
                'date': f'2025-05-0{i + 1}',
                'rating': (i + 1)
            })
            db.commit()
        response = client.get('/learned')
        assert response.status_code == 200
        response_text = response.data.decode('utf-8')
        for i in range(3):
            assert f"Dance {i}" in response_text
            assert f"data-rating=\"{i + 1}\"" in response_text
            assert f"Finished learning: 2025-05-0{i + 1}" in response_text

