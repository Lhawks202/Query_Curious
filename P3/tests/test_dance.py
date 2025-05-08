import json
from dances.db import get_db
from flask import Flask
from flask.testing import FlaskClient
from typing import Any
'''
def test_add_dance(client: FlaskClient, app: Flask, auth: Any, insert: Any) -> None:
    with app.app_context():
        auth.register()
        auth.login()
        figure_id = insert.insert_figure(
            name="Test Figure",
            roles="Lead, Follow",
            start_position="Closed",
            action="Turn",
            end_position="Open",
            duration=5
        )
        response = client.post('/dance/', data={
            'dance_data': json.dumps({
                'danceName': 'Test Dance',
                'source': 'Test Source',
                'video': 'test.mp4',
                'steps': [
                    {
                        'stepName': 'A',
                        'figures': ['Test Figure']
                    }
                ]
            })
        }, follow_redirects=True)
    assert response.status_code == 200
    with app.app_context():
        db = get_db()
        dance = db.execute("SELECT * FROM Dance WHERE DanceName = ?", ('Test Dance',)).fetchone()
        assert dance is not None
        assert dance['Source'] == 'Test Source'
        assert dance['Video'] == 'test.mp4'
        step = db.execute("SELECT * FROM Step WHERE DanceID = ?", (dance['ID'],)).fetchone()
        assert step is not None
        assert step['StepName'] == 'Step 1'
        figure_step = db.execute("SELECT * FROM FigureStep WHERE StepsId = ?", (step['ID'],)).fetchone()
        assert figure_step is not None
        assert figure_step['FigureId'] == figure_id
'''
def test_create_figure_endpoint(client: FlaskClient, app: Flask, auth: Any) -> None:
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
'''
def test_search_figures(client: FlaskClient, app: Flask, auth: Any, insert: Any) -> None:
    with app.app_context():
        auth.register()
        auth.login()
        insert.insert_figure(name="Turn", roles="Lead", start_position="Closed", action="Spin", end_position="Open", duration=5)
        insert.insert_figure(name="Slide", roles="Follow", start_position="Open", action="Glide", end_position="Closed", duration=3)
    response = client.post('/dance/search', json={'q': 'Turn'})
    assert response.status_code == 200
    results = response.get_json()
    assert len(results) == 1
    assert results[0]['name'] == 'Turn'
    response = client.post('/dance/search', json={'q': 'Jump'})
    assert response.status_code == 200
    results = response.get_json()
    assert len(results) == 0

def test_display_information(client: FlaskClient, app: Flask, auth: Any, insert: Any) -> None:
    with app.app_context():
        auth.register()
        auth.login()
        dance_id = insert.insert_dance(dance_name="Test Dance", video="test.mp4", source="Test Source")
        step_id = insert.insert_step(dance_id=dance_id, step_name="Step 1")
        figure_id = insert.insert_figure(
            name="Test Figure",
            roles="Lead, Follow",
            start_position="Closed",
            action="Turn",
            end_position="Open",
            duration=5
        )
        insert.insert_figure_step(step_id=step_id, figure_id=figure_id, place=1)
    response = client.get(f'/dance/{dance_id}')
    assert response.status_code == 200
    response_text = response.data.decode('utf-8')
    assert "Test Dance" in response_text
    assert "Step 1" in response_text
    assert "Test Figure" in response_text
    assert "Lead, Follow" in response_text
    assert "Closed" in response_text
    assert "Turn" in response_text
    assert "Open" in response_text
'''