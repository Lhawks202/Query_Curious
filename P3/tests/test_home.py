from flask import g, session
from dances.db import get_db

def test_index_no_user(client):
    response = client.get('/')
    assert response.status_code == 200, "Internal Server Error Index"
    response_text = response.data.decode('utf-8')
    assert '<h5 class="card-title">Dance Name</h5>' in response_text
    assert '<h5 class="card-title">Unknown Dance</h5>' in response_text
    assert '<h5 class="card-title">The Gypsy Orbit</h5>' in response_text
    assert 'Source: ins_anna_maria.json' in response_text
    assert 'Source: ins_apley_house.json' in response_text
    assert 'Source: ins_astonished_archeologist.json' in response_text
    assert '<button type="button" class="btn btn-sm btn-warning"' not in response_text
    assert '<button type="button" class="btn btn-sm btn-outline-warning"' not in response_text
    assert '<button type="button" class="btn btn-sm btn-danger"' not in response_text
    assert '<button type="button" class="btn btn-sm btn-outline-danger"' not in response_text

def test_index_user(client, auth):
    auth.register()
    auth.login()
    with client:
        response = client.get('/')
        assert response.status_code == 200, "Internal Server Error For Index Login"
        response_text = response.data.decode('utf-8')
        assert '<h5 class="card-title">Dance Name</h5>' in response_text
        assert '<h5 class="card-title">Unknown Dance</h5>' in response_text
        assert '<h5 class="card-title">The Gypsy Orbit</h5>' in response_text
        assert 'Source: ins_anna_maria.json' in response_text
        assert 'Source: ins_apley_house.json' in response_text
        assert 'Source: ins_astonished_archeologist.json' in response_text
        assert '<button type="button" class="btn btn-sm btn-warning"' in response_text
        assert '<button type="button" class="btn btn-sm btn-outline-warning"' in response_text
        assert '<button type="button" class="btn btn-sm btn-danger"' in response_text
        assert '<button type="button" class="btn btn-sm btn-outline-danger"' in response_text

def test_index_with_valid_search(client):
    response = client.get('/?search=The Gypsy Orbit')
    assert response.status_code == 200, "Internal Server Error on search"
    response_text = response.data.decode('utf-8')
    assert 'The Gypsy Orbit' in response_text
    assert 'Unknown Dance' not in response_text

def test_index_with_invalid_search(client):
    """Test the index route with an invalid search query."""
    response = client.get('/?search=NonExistentDance')
    assert response.status_code == 200, "Internal Server Error on search"
    response_text = response.data.decode('utf-8')
    assert 'The Gypsy Orbit' not in response_text
    assert 'Unknown Dance' not in response_text
    assert 'No results found' in response_text