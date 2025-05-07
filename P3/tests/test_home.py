from flask import g, session
from dances.db import get_db

def test_index_no_user(client):
    response = client.get('/')      
    assert response.status_code == 200, "Internal Server Error Index"
    response_text = response.data.decode('utf-8')
    assert '<h5 class="card-title">Adieu</h5>' in response_text
    assert '<h5 class="card-title">Alice</h5>' in response_text
    assert '<h5 class="card-title">All In A Garden Green</h5>' in response_text
    assert 'Source: ins_adieu.json' in response_text
    assert 'Source: ins_alice.json' in response_text
    assert 'Source: ins_all_in_a_garden_green.json' in response_text
    assert 'Register' in response_text
    assert 'Log In' in response_text
    assert 'My Profile' not in response_text
    assert 'My Favorites' not in response_text
    assert 'My Learning' not in response_text

def test_index_user(client, auth):
    auth.register()
    auth.login()
    with client:
        response = client.get('/')
        assert response.status_code == 200, "Internal Server Error For Index Login"
        response_text = response.data.decode('utf-8')
        assert '<h5 class="card-title">Adieu</h5>' in response_text
        assert '<h5 class="card-title">Alice</h5>' in response_text
        assert '<h5 class="card-title">All In A Garden Green</h5>' in response_text
        assert 'Source: ins_adieu.json' in response_text
        assert 'Source: ins_alice.json' in response_text
        assert 'Source: ins_all_in_a_garden_green.json' in response_text
        assert 'Register' not in response_text
        assert 'Log In' not in response_text
        assert 'My Profile' in response_text
        assert 'My Favorites' in response_text
        assert 'Learning List' in response_text

def test_index_with_valid_search(client):
    response = client.get('/?search=The Gypsy Orbit')
    assert response.status_code == 200, "Internal Server Error on search"
    response_text = response.data.decode('utf-8')
    assert 'The Gypsy Orbit' in response_text
    assert 'All In A Garden Green' not in response_text

def test_index_with_invalid_search(client):
    """Test the index route with an invalid search query."""
    response = client.get('/?search=NonExistentDance')
    assert response.status_code == 200, "Internal Server Error on search"
    response_text = response.data.decode('utf-8')
    assert 'The Gypsy Orbit' not in response_text
    assert 'All In A Garden Green' not in response_text
    assert 'No dances found matching \"NonExistentDance\".' in response_text