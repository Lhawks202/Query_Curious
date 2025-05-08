import json
from dances.db import get_db
from flask import Flask
from flask.testing import FlaskClient
from typing import Any

def test_edit_dance(client: FlaskClient, app: Flask, auth: Any, insert: Any) -> None:
    with app.app_context():
        auth.register()
        auth.login()
        dance_id = insert.insert_dance(dance_name="Original Dance", video="original.mp4", source="Original Source")
        step_id = insert.insert_step(dance_id=dance_id, step_name="Original Step")
        figure_id = insert.insert_figure(name="Original Figure", roles="Lead", start_position="Closed", action="Turn", end_position="Open", duration=5)
        insert.insert_figure_step(step_id=step_id, figure_id=figure_id, place=0)
    updated_data = {
        "danceName": "Updated Dance",
        "video": "updated.mp4",
        "source": "Updated Source",
        "steps": [
            {
                "stepName": "Updated Step",
                "figures": ["Original Figure"]
            }
        ]
    }
    response = client.post(f'/dance/edit/{dance_id}', data={
        'dance_data': json.dumps(updated_data)
    }, headers={'X-Requested-With': 'XMLHttpRequest'})
    assert response.status_code == 200
    response_json = response.get_json()
    assert response_json['status'] == 'success'
    assert response_json['message'] == 'Dance updated successfully'
    with app.app_context():
        db = get_db()
        dance = db.execute("SELECT * FROM Dance WHERE ID = ?", (dance_id,)).fetchone()
        assert dance['DanceName'] == "Updated Dance"
        assert dance['Video'] == "updated.mp4"
        assert dance['Source'] == "Updated Source"
        step = db.execute("SELECT * FROM Step WHERE DanceID = ?", (dance_id,)).fetchone()
        assert step['StepName'] == "Updated Step"
        figure_step = db.execute("SELECT * FROM FigureStep WHERE StepId = ?", (step['ID'],)).fetchone()
        assert figure_step['FigureId'] == figure_id

def test_add_dance(client: FlaskClient, app: Flask, auth: Any, insert: Any) -> None:
    auth.register()
    auth.login()
    new_dance_data = {
        "danceName": "New Dance",
        "video": "new.mp4",
        "source": "New Source",
        "steps": [
            {
                "stepName": "Step 1",
                "figures": ["Figure 1"]
            }
        ]
    }
    with app.app_context():
        insert.insert_figure(name="Figure 1", roles="Lead", start_position="Closed", action="Turn", end_position="Open", duration=5)
    response = client.post('/dance/create', data={
        'dance_data': json.dumps(new_dance_data)
    }, headers={'X-Requested-With': 'XMLHttpRequest'})
    assert response.status_code == 201
    response_json = response.get_json()
    assert response_json['status'] == 'success'
    assert response_json['message'] == 'Dance created successfully'
    with app.app_context():
        db = get_db()
        dance = db.execute("SELECT * FROM Dance WHERE DanceName = ?", ("New Dance",)).fetchone()
        assert dance is not None
        assert dance['Video'] == "new.mp4"
        assert dance['Source'] == "New Source"
        step = db.execute("SELECT * FROM Step WHERE DanceID = ?", (dance['ID'],)).fetchone()
        assert step['StepName'] == "Step 1"
        figure_step = db.execute("SELECT * FROM FigureStep WHERE StepId = ?", (step['ID'],)).fetchone()
        assert figure_step is not None

def test_create_figure(client: FlaskClient, app: Flask, auth: Any) -> None:
    auth.register()
    auth.login()
    response = client.post('/dance/create_figure', json={
        'name': 'Test Figure',
        'roles': 'Lead, Follow',
        'start_position': 'Closed',
        'action': 'Turn',
        'end_position': 'Open',
        'duration': 5
    })
    assert response.status_code == 201
    response_json = response.get_json()
    assert response_json['name'] == 'Test Figure'
    with app.app_context():
        db = get_db()
        figure = db.execute("SELECT * FROM Figure WHERE Name = ?", ('Test Figure',)).fetchone()
        assert figure is not None
        assert figure['Roles'] == 'Lead, Follow'
        assert figure['StartPosition'] == 'Closed'
        assert figure['Action'] == 'Turn'
        assert figure['EndPosition'] == 'Open'
        assert figure['Duration'] == 5

def test_search_figures(client: FlaskClient, app: Flask, auth: Any, insert: Any) -> None:
    with app.app_context():
        auth.register()
        auth.login()
        insert.insert_figure(name="Turn", roles="Lead", start_position="Closed", action="Spin", end_position="Open", duration=5)
        insert.insert_figure(name="Slide", roles="Follow", start_position="Open", action="Glide", end_position="Closed", duration=3)
    response = client.post('/dance/search', json={'q': 'turn'})
    assert response.status_code == 200
    results = response.get_json()
    assert len(results) != 0
    response = client.post('/dance/search', json={'q': 'BADBADBADBADBAD'})
    assert response.status_code == 200
    results = response.get_json()
    assert len(results) == 0

def test_display_information(client: FlaskClient, app: Flask, auth: Any, insert: Any) -> None:
    with app.app_context():
        auth.register()
        auth.login()
        dance_id = insert.insert_dance(dance_name="Test Dance", video="test.mp4", source="Test Source")
        step_id = insert.insert_step(dance_id=dance_id, step_name="Step 1")
        figure_id = insert.insert_figure(name="Test Figure", roles="Lead", start_position="Closed", action="Turn", end_position="Open", duration=5)
        insert.insert_figure_step(step_id=step_id, figure_id=figure_id, place=1)
    response = client.get(f'/dance/{dance_id}')
    assert response.status_code == 200
    response_text = response.data.decode('utf-8')
    assert 'Test Dance' in response_text
    assert '{"action": "Turn", "duration": 5, "end_position": "Open", "name": "Test Figure", "start_position": "Closed"}}' in response_text
